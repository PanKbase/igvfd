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
import requests


_marker = object()


def includeme(config):
    config.scan(__name__, categories=None)
    config.add_route('signup', 'signup')
    config.add_route('login', 'login')
    config.add_route('login-trailing', 'login/')  # Handle trailing slash
    config.add_route('logout', 'logout')
    config.add_route('session', 'session')
    config.add_route('session-properties', 'session-properties')
    config.add_route('impersonate-user', 'impersonate-user')


AUTH0_DOMAIN = 't2depi.auth0.com'


class LoginDenied(HTTPForbidden):
    title = 'Login failure'


class Auth0AuthenticationPolicy(CallbackAuthenticationPolicy):
    """
    Checks assertion during authentication so login can construct user session.
    """
    login_path = '/login'
    method = 'POST'

    def unauthenticated_userid(self, request):

        # Handle both /login and /login/ paths
        normalized_path = request.path.rstrip('/')
        if request.method != self.method or normalized_path != self.login_path:
            return None

        cached = getattr(request, '_auth0_authenticated', _marker)
        if cached is not _marker:
            return cached

        try:
            access_token = request.json['accessToken']
            if not access_token:
                if self.debug:
                    self._log(
                        'Empty access token provided.',
                        'unauthenticated_userid',
                        request)
                request._auth0_authenticated = None
                return None
        except (ValueError, TypeError, KeyError) as e:
            if self.debug:
                self._log(
                    ('Missing or invalid access token: %s (%s)', (e, type(e).__name__)),
                    'unauthenticated_userid',
                    request)
            request._auth0_authenticated = None
            return None

        try:
            user_url = 'https://{domain}/userinfo'.format(domain=AUTH0_DOMAIN)
            headers = {'Authorization': 'Bearer {access_token}'.format(access_token=access_token)}
            response = requests.get(user_url, headers=headers, timeout=10)
            if response.status_code != 200:
                # Log the error for debugging (even if debug mode is off, log critical auth failures)
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(
                    'Auth0 userinfo returned status %d for login attempt: %s',
                    response.status_code,
                    response.text[:200]  # Limit log size
                )
                if self.debug:
                    self._log(
                        ('Auth0 userinfo returned status %d: %s', (response.status_code, response.text)),
                        'unauthenticated_userid',
                        request)
                request._auth0_authenticated = None
                return None
            try:
                user_info = response.json()
            except ValueError as json_error:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(
                    'Auth0 userinfo returned invalid JSON: %s',
                    response.text[:200]
                )
                request._auth0_authenticated = None
                return None
        except requests.exceptions.Timeout as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error('Auth0 userinfo request timed out: %s', e)
            if self.debug:
                self._log(
                    ('Auth0 request timed out: %s', e),
                    'unauthenticated_userid',
                    request)
            request._auth0_authenticated = None
            return None
        except requests.exceptions.RequestException as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error('Auth0 request failed: %s (%s)', e, type(e).__name__)
            if self.debug:
                self._log(
                    ('Auth0 request failed: %s (%s)', (e, type(e).__name__)),
                    'unauthenticated_userid',
                    request)
            request._auth0_authenticated = None
            return None
        except (ValueError, KeyError) as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error('Invalid Auth0 response format: %s (%s)', e, type(e).__name__)
            if self.debug:
                self._log(
                    ('Invalid Auth0 response format: %s (%s)', (e, type(e).__name__)),
                    'unauthenticated_userid',
                    request)
            request._auth0_authenticated = None
            return None

        if not user_info.get('email_verified'):
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(
                'Email not verified for user: %s',
                user_info.get('email', 'unknown')
            )
            if self.debug:
                self._log(
                    ('Email not verified for user: %s', user_info.get('email', 'unknown')),
                    'unauthenticated_userid',
                    request)
            request._auth0_authenticated = None
            return None

        email = user_info.get('email')
        if not email:
            import logging
            logger = logging.getLogger(__name__)
            logger.error('No email in Auth0 userinfo response: %s', user_info)
            if self.debug:
                self._log(
                    ('No email in Auth0 userinfo response'),
                    'unauthenticated_userid',
                    request)
            request._auth0_authenticated = None
            return None

        email = request._auth0_authenticated = email.lower()
        return email

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
    user_data_request = requests.get(url, headers=headers)
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
@view_config(route_name='login', request_method='POST',
             permission=NO_PERMISSION_REQUIRED)
@view_config(route_name='login-trailing', request_method='POST',
             permission=NO_PERMISSION_REQUIRED)
def login(request):
    """View to check the auth0 assertion and remember the user"""
    import logging
    logger = logging.getLogger(__name__)
    
    # Check if request body can be parsed
    try:
        request_body = request.json
    except (ValueError, TypeError) as e:
        logger.error('Failed to parse login request JSON: %s', e)
        raise HTTPBadRequest(explanation='Invalid JSON in request body')
    
    # Check if accessToken is present
    if not request_body or 'accessToken' not in request_body:
        logger.warning('Login request missing accessToken')
        raise HTTPBadRequest(explanation='Missing accessToken in request body')
    
    login = request.authenticated_userid
    if login is None:
        namespace = userid = None
        logger.warning('Authentication failed: authenticated_userid is None')
    else:
        try:
            namespace, userid = login.split('.', 1)
        except ValueError:
            logger.error('Invalid authenticated_userid format: %s', login)
            namespace = userid = None

    # create new user account if one does not exist
    if namespace != 'auth0':
        logger.warning('Login denied: namespace is %s, expected auth0', namespace)
        request.session.invalidate()
        request.response.headerlist.extend(forget(request))
        raise LoginDenied()

    request.session.invalidate()
    request.session.get_csrf_token()
    request.response.headerlist.extend(remember(request, 'mailto.' + userid))

    properties = request.embed('/session-properties', as_user=userid)
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
