from snovault import COLLECTIONS
from snovault.calculated import calculate_properties
from snovault.validation import ValidationFailure
from snovault.validators import no_validate_item_content_post
from operator import itemgetter
from snovault.crud_views import collection_add
from snovault.schema_utils import validate_request
from pyramid.authentication import CallbackAuthenticationPolicy
from igvfd.types.user import User
from jsonschema.exceptions import ValidationError
from pyramid.httpexceptions import (
    HTTPBadRequest,
    HTTPInternalServerError,
    HTTPForbidden,
    HTTPFound,
    HTTPUnauthorized,
)
from pyramid.security import (
    remember,
    forget,
)
from pyramid.security import NO_PERMISSION_REQUIRED
from pyramid.settings import (
    asbool,
    aslist,
)
from pyramid.traversal import find_resource
from pyramid.view import (
    view_config,
)
import os
import requests
import logging


_marker = object()


def includeme(config):
    config.scan(__name__, categories=None)
    config.add_route('signup', '/signup{slash:/?}')
    config.add_route('login', '/login{slash:/?}')
    config.add_route('logout', '/logout{slash:/?}')
    config.add_route('session', '/session{slash:/?}')
    config.add_route('session-properties', '/session-properties{slash:/?}')
    config.add_route('impersonate-user', '/impersonate-user{slash:/?}')


AUTH0_DOMAIN = os.environ.get('AUTH0_DOMAIN', 't2depi.auth0.com')


class LoginDenied(HTTPForbidden):
    title = 'Login failure'


class Auth0AuthenticationPolicy(CallbackAuthenticationPolicy):
    """
    Checks assertion during authentication so login can construct user session.
    """
    login_path = '/login'
    method = 'POST'

    def unauthenticated_userid(self, request):
        # Do not call Auth0 from the authentication policy. On production,
        # invoking /userinfo here during POST /login hard-crashes into an
        # HTML 500. The login view validates tokens directly and may set
        # request._auth0_authenticated for callers that still expect it.
        cached = getattr(request, '_auth0_authenticated', _marker)
        if cached is not _marker:
            return cached
        return None

    def remember(self, request, principal, **kw):
        return []

    def forget(self, request):
        return []


@view_config(context=User.Collection, request_method='POST', permission='signup', name='sign-up')
def signup(context, request):
    """
    Create new user.
    :param request: Pyramid request object
    """
    access_token = request.json.get('accessToken')
    if not access_token:
        raise HTTPBadRequest(explanation='Access token required')
    url = 'https://{domain}/userinfo'.format(domain=AUTH0_DOMAIN)
    headers = {'Authorization': 'Bearer {access_token}'.format(access_token=access_token)}
    user_data_request = requests.get(url, headers=headers, timeout=10)
    if user_data_request.status_code != 200:
        raise HTTPBadRequest(explanation='Could not get user data')
    user_data = user_data_request.json()
    if user_data['email_verified'] is not True:
        raise HTTPBadRequest(explanation='Unverified email')
    user_info = _get_user_info(user_data)
    validate_request(context.type_info.schema, request, user_info)
    if request.errors:
        raise ValidationError(', '.join(request.errors))
    result = collection_add(context, request, user_info)
    if not result or result['status'] != 'success':
        raise HTTPInternalServerError(explanation='attempt to create account was not successful')
    return result


def _get_first_and_last_names_from_name(name):
    """
    Get user first and last name from name.
        :param name: name object.
    """
    if not name or not name.strip():
        return None, None
    name = name.strip()
    name_split = name.split(' ')
    name_length = len(name_split)
    first_name = name_split[0]
    last_name = name_split[-1] if name_length > 1 else None
    return first_name, last_name


def _get_user_info(user_data):
    """
    get user info from user_data object
        :param user_data: user_data object from oauth service
    """
    if not user_data:
        raise ValidationError('No user data provided')
    if not user_data.get('email') or not user_data.get('email').strip():
        raise ValidationError('No e-mail provided')
    first_name, last_name = _get_first_and_last_names_from_name(user_data.get('name'))
    return {
        'email': user_data['email'],
        'first_name': user_data.get('given_name') or user_data.get('first_name') or first_name,
        'last_name': user_data.get('family_name') or user_data.get('last_name') or last_name or user_data.get('email').split('@')[0],
    }


# Unfortunately, X-Requested-With is not sufficient.
# http://lists.webappsec.org/pipermail/websecurity_lists.webappsec.org/2011-February/007533.html
# Checking the CSRF token in middleware is easier
def _login_denied_response(request, detail=None):
    """
    Fail login with a JSON error response.

    Do not raise HTTPForbidden/LoginDenied — snovault's refresh_session
    exception view for Forbidden returns HTML 500 on this deployment.
    Do not return a dict with status_code=403 either — that also 500s on
    production (observed on 41.0.1 and 41.0.2). HTTPUnauthorized uses the
    working http_error exception view (same path as HTTPBadRequest).
    """
    message = detail or 'Login failure'
    raise HTTPUnauthorized(explanation='%s (igvfd-41.0.3)' % message)


def _auth0_email_from_access_token(access_token):
    """
    Validate an Auth0 access token via /userinfo and return the verified email.
    Returns (email, error_detail). On success error_detail is None.
    """
    logger = logging.getLogger(__name__)
    if not access_token:
        return None, 'Empty access token.'
    try:
        user_url = 'https://{domain}/userinfo'.format(domain=AUTH0_DOMAIN)
        headers = {
            'Authorization': 'Bearer {access_token}'.format(
                access_token=access_token
            )
        }
        response = requests.get(user_url, headers=headers, timeout=10)
    except requests.exceptions.Timeout:
        logger.exception('Auth0 userinfo timed out during login')
        return None, 'Auth0 userinfo request timed out.'
    except requests.exceptions.RequestException:
        logger.exception('Auth0 userinfo request failed during login')
        return None, 'Auth0 userinfo request failed.'

    if response.status_code != 200:
        logger.warning(
            'Auth0 userinfo returned status %d during login: %s',
            response.status_code,
            (response.text or '')[:200],
        )
        return None, 'Auth0 rejected the access token (userinfo status %d).' % (
            response.status_code,
        )

    try:
        user_info = response.json()
    except ValueError:
        logger.error(
            'Auth0 userinfo returned invalid JSON during login: %s',
            (response.text or '')[:200],
        )
        return None, 'Auth0 userinfo returned invalid JSON.'

    if not user_info.get('email_verified'):
        return None, 'Auth0 email is not verified.'

    email = user_info.get('email')
    if not email or not str(email).strip():
        return None, 'Auth0 userinfo did not include an email.'

    return str(email).strip().lower(), None


def _safe_refresh_session(exc, request):
    """Render Forbidden/CSRF errors as JSON even if session refresh fails."""
    from snovault import validation as snovault_validation

    logger = logging.getLogger(__name__)
    try:
        request.session.get_csrf_token()
        request.session.changed()
    except Exception:
        logger.exception(
            'Session refresh failed while rendering %s',
            type(exc).__name__,
        )
    try:
        return snovault_validation.http_error(exc, request)
    except Exception:
        logger.exception(
            'http_error failed while rendering %s',
            type(exc).__name__,
        )
        request.response.status_code = getattr(exc, 'code', 400) or 400
        return {
            '@type': [type(exc).__name__, 'Error'],
            'status': 'error',
            'code': getattr(exc, 'code', 400) or 400,
            'title': getattr(exc, 'title', 'Error'),
            'description': getattr(exc, 'explanation', None) or str(exc),
        }


def patch_snovault_error_views():
    """
    Replace snovault's refresh_session before snovault is included, so CSRF /
    Forbidden errors return JSON instead of HTML 500.
    """
    from snovault import validation as snovault_validation

    snovault_validation.refresh_session = _safe_refresh_session


@view_config(route_name='login', request_method='POST',
             permission=NO_PERMISSION_REQUIRED)
def login(request):
    """View to check the auth0 assertion and remember the user"""
    logger = logging.getLogger(__name__)

    try:
        request_body = request.json
    except (ValueError, TypeError) as e:
        logger.error('Failed to parse login request JSON: %s', e)
        raise HTTPBadRequest(explanation='Invalid JSON in request body')

    if not request_body or 'accessToken' not in request_body:
        logger.warning('Login request missing accessToken')
        raise HTTPBadRequest(explanation='Missing accessToken in request body')

    # Validate Auth0 inline (same approach as signup). Do not call
    # request.authenticated_userid here — that path hard-crashes this
    # deployment into an HTML 500 even when Auth0 correctly rejects the token.
    try:
        email, auth_error = _auth0_email_from_access_token(
            request_body.get('accessToken')
        )
    except Exception:
        logger.exception('Unexpected failure validating Auth0 token during login')
        return _login_denied_response(
            request,
            detail='Auth0 token validation failed on the server.',
        )

    if auth_error or not email:
        logger.warning('Login denied: %s', auth_error)
        return _login_denied_response(
            request,
            detail=auth_error or 'Auth0 token validation failed.',
        )

    users = request.registry[COLLECTIONS]['user']
    try:
        user = users[email]
    except KeyError:
        logger.warning('Login denied: no portal user for %s', email)
        return _login_denied_response(
            request,
            detail=(
                'Auth0 succeeded but this email is not a current portal user. '
                'Ask an admin to create your User account.'
            ),
        )

    if user.properties.get('status') != 'current':
        logger.warning(
            'Login denied: user %s status=%s',
            email,
            user.properties.get('status'),
        )
        return _login_denied_response(
            request,
            detail='Auth0 succeeded but this portal user is not current.',
        )

    userid = email
    try:
        request.session.invalidate()
        request.session.get_csrf_token()
        request.response.headerlist.extend(remember(request, 'mailto.' + userid))
        properties = request.embed('/session-properties', as_user=userid)
    except Exception:
        logger.exception('Failed to establish session for user %s', email)
        return _login_denied_response(
            request,
            detail='Auth0 succeeded but establishing the portal session failed.',
        )

    if 'auth.userid' in request.session:
        properties['auth.userid'] = request.session['auth.userid']

    return properties


@view_config(route_name='logout',
             permission=NO_PERMISSION_REQUIRED, http_cache=0)
def logout(request):
    """View to forget the user"""
    request.session.invalidate()
    request.session.get_csrf_token()
    request.response.headerlist.extend(forget(request))
    if asbool(request.params.get('redirect', True)):
        raise HTTPFound(location=request.resource_path(request.root))
    return {}


@view_config(route_name='session-properties', request_method='GET',
             permission=NO_PERMISSION_REQUIRED)
def session_properties(request):
    for principal in request.effective_principals:
        if principal.startswith('userid.'):
            break
    else:
        return {}

    namespace, userid = principal.split('.', 1)
    user = request.registry[COLLECTIONS]['user'][userid]
    user_actions = calculate_properties(user, request, category='user_action')

    properties = {
        'user': request.embed(request.resource_path(user)),
        'user_actions': [v for k, v in sorted(user_actions.items(), key=itemgetter(0))],
        'admin': 'group.admin' in request.effective_principals
    }

    if 'auth.userid' in request.session:
        properties['auth.userid'] = request.session['auth.userid']

    return properties


@view_config(route_name='session', request_method='GET',
             permission=NO_PERMISSION_REQUIRED)
def session(request):
    request.session.get_csrf_token()
    return request.session


@view_config(route_name='impersonate-user', request_method='POST',
             validators=[no_validate_item_content_post],
             permission='impersonate')
def impersonate_user(request):
    """As an admin, impersonate a different user."""
    user = request.validated['user']

    try:
        user = find_resource(request.root, user)
    except KeyError:
        raise ValidationFailure('body', ['user'], 'User not found.')

    if user.item_type != 'user':
        raise ValidationFailure('body', ['user'], 'User not found.')
    if user.properties.get('status') != 'current':
        raise ValidationFailure('body', ['user'], 'User is not enabled.')

    request.session.invalidate()
    request.session.get_csrf_token()
    request.response.headerlist.extend(
        remember(request, 'mailto.%s' % user.uuid))
    user_properties = request.embed(
        '/session-properties', as_user=str(user.uuid))
    if 'auth.userid' in request.session:
        user_properties['auth.userid'] = request.session['auth.userid']

    return user_properties
