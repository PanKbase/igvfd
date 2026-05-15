"""
AWS Bedrock Agent integration for natural language queries.
"""
import json
import logging
import re
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPBadRequest, HTTPInternalServerError
from boto3 import client as boto3_client

logger = logging.getLogger(__name__)

# Security constants
MAX_QUERY_LENGTH = 2000
MAX_RESPONSE_LENGTH = 10000
SUSPICIOUS_PATTERNS = [
    r'ignore\s+(previous|all|above)\s+instructions?',
    r'system\s+prompt',
    r'you\s+are\s+now',
    r'forget\s+(everything|all)',
    r'override\s+(system|instructions)',
]


def includeme(config):
    """Include Bedrock agent routes."""
    config.add_route('bedrock-agent-query', '/bedrock-agent/query{slash:/?}')
    config.scan(__name__)


def get_bedrock_client(request):
    """Get Bedrock Runtime client with proper configuration."""
    region = request.registry.settings.get('aws.region', 'us-east-1')
    return boto3_client('bedrock-runtime', region_name=region)


def sanitize_query(query: str) -> str:
    """
    Sanitize user query to prevent prompt injection attacks.
    
    Returns sanitized query or raises HTTPBadRequest if suspicious.
    """
    if not isinstance(query, str):
        raise HTTPBadRequest(json_body={'error': 'Query must be a string'})
    
    # Remove control characters (except newline, tab, carriage return)
    query = ''.join(char for char in query if ord(char) >= 32 or char in '\n\r\t')
    
    # Limit length
    if len(query) > MAX_QUERY_LENGTH:
        raise HTTPBadRequest(
            json_body={'error': f'Query too long (max {MAX_QUERY_LENGTH} characters)'}
        )
    
    # Check for suspicious patterns (log but don't block - let Guardrails handle)
    query_lower = query.lower()
    for pattern in SUSPICIOUS_PATTERNS:
        if re.search(pattern, query_lower):
            logger.warning(
                f"Suspicious query pattern detected: {pattern}",
                extra={'query_preview': query[:100]}
            )
    
    return query.strip()


def validate_response(response_text: str) -> str:
    """
    Validate and sanitize AI response.
    
    Returns validated response, truncated if necessary.
    """
    if not isinstance(response_text, str):
        return ""
    
    # Limit response length
    if len(response_text) > MAX_RESPONSE_LENGTH:
        logger.warning(f"Response truncated from {len(response_text)} to {MAX_RESPONSE_LENGTH} characters")
        return response_text[:MAX_RESPONSE_LENGTH] + "... (response truncated)"
    
    # Remove potential script tags
    response_text = re.sub(
        r'<script[^>]*>.*?</script>',
        '',
        response_text,
        flags=re.DOTALL | re.IGNORECASE
    )
    
    return response_text


def get_system_prompt():
    """Get the system prompt for the Bedrock agent."""
    return """You are an AI assistant helping users query the PanKbase API.

The PanKbase API is available at: https://api.data.pankbase.org/

For complete API documentation, refer to the OpenAPI specification:
https://pankbase.github.io/pankbase-client-openapi-spec/

Key API endpoints:
- GET /analysis-sets/{id}/ - Get analysis set details including files, samples, donors
- GET /files/{id}/ - Get file details including version, note, format, size
- GET /search/?type=File&file_set={file_set_id} - Search files by file set
- GET /search/?type=AnalysisSet - Search analysis sets
- GET /search/?type=File&file_format={format} - Search files by format

Important API features:
- Files have version and note fields for tracking changes
- All file versions (including replaced) are visible in file sets
- Use file_set parameter to find all files in an analysis set
- Responses are in JSON-LD format with @id, @type, and other properties

When answering queries:
1. Reference the OpenAPI spec for accurate endpoint details
2. Provide specific API endpoint examples with actual accession IDs when possible
3. Include relevant links to https://data.pankbase.org/ for user navigation
4. Explain how to use the API endpoints to get the requested information
5. Mention file versioning when relevant (version and note fields)

Example API calls:
- GET https://api.data.pankbase.org/analysis-sets/PKBDS1349YHGQ/
- GET https://api.data.pankbase.org/search/?type=File&file_set=/analysis-sets/PKBDS1349YHGQ/

Common use cases:
- File versions: Files have version and note fields. All versions appear in the file_set listing.
- Analysis sets: Use /analysis-sets/{id}/ to get details including files, samples, and donors.
- File formats: Common formats include mtx, h5ad, bam, bed, etc. Use search with file_format parameter.
"""


@view_config(route_name='bedrock-agent-query', request_method='POST', permission='view')
def bedrock_agent_query(request):
    """
    Natural language query endpoint using AWS Bedrock.
    
    POST /bedrock-agent/query
    Body: {"query": "How many files are in analysis set PKBDS1349YHGQ?"}
    
    Returns:
    {
        "query": "user query",
        "response": "AI response",
        "model": "model_id"
    }
    """
    try:
        # Get query from request
        if not hasattr(request, 'json_body'):
            raise HTTPBadRequest(json_body={'error': 'Request body must be JSON'})
        
        body = request.json_body
        user_query = body.get('query', '')
        
        # Sanitize and validate input
        user_query = sanitize_query(user_query)
        
        if not user_query:
            raise HTTPBadRequest(json_body={'error': 'Query parameter is required and cannot be empty'})
        
        # Get configuration from settings
        model_id = request.registry.settings.get(
            'bedrock.model_id',
            'anthropic.claude-3-5-sonnet-20241022-v2:0'
        )
        
        # Get Bedrock client
        bedrock_runtime = get_bedrock_client(request)
        
        # Prepare the prompt
        system_prompt = get_system_prompt()
        
        # Prepare messages
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": user_query
                    }
                ]
            }
        ]
        
        # Get guardrail configuration if available
        guardrail_config = {}
        guardrail_id = request.registry.settings.get('bedrock.guardrail_id')
        if guardrail_id:
            guardrail_config = {
                'guardrailIdentifier': guardrail_id,
                'guardrailVersion': request.registry.settings.get(
                    'bedrock.guardrail_version',
                    'DRAFT'
                )
            }
        
        # Call Bedrock
        try:
            response = bedrock_runtime.invoke_model(
                modelId=model_id,
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 4096,
                    "system": system_prompt,
                    "messages": messages,
                    **guardrail_config  # Include guardrails if configured
                }),
                contentType="application/json",
                accept="application/json"
            )
            
            # Check for guardrail blocks in response headers
            response_metadata = response.get('ResponseMetadata', {})
            headers = response_metadata.get('HTTPHeaders', {})
            guardrail_action = headers.get('x-amazon-bedrock-guardrail-action')
            
            if guardrail_action == 'BLOCKED':
                logger.warning(
                    "Query blocked by guardrails",
                    extra={'query_preview': user_query[:100]}
                )
                raise HTTPBadRequest(
                    json_body={
                        'error': 'Query blocked by content filter. Please rephrase your question.',
                        'reason': 'Content policy violation'
                    }
                )
        except Exception as bedrock_error:
            logger.error(f"Bedrock API error: {str(bedrock_error)}", exc_info=True)
            raise HTTPInternalServerError(
                json_body={
                    'error': 'Failed to communicate with Bedrock service',
                    'detail': str(bedrock_error)
                }
            )
        
        # Parse response
        response_body = json.loads(response['body'].read())
        
        # Extract assistant message
        assistant_message = ""
        for content_block in response_body.get('content', []):
            if content_block.get('type') == 'text':
                assistant_message += content_block.get('text', '')
        
        if not assistant_message:
            assistant_message = "I couldn't generate a response. Please try rephrasing your question."
        
        # Validate and sanitize response
        assistant_message = validate_response(assistant_message)
        
        return {
            'query': user_query,
            'response': assistant_message,
            'model': model_id
        }
        
    except HTTPBadRequest:
        raise
    except HTTPInternalServerError:
        raise
    except Exception as e:
        logger.error(f"Bedrock agent error: {str(e)}", exc_info=True)
        raise HTTPInternalServerError(
            json_body={
                'error': 'An unexpected error occurred',
                'detail': str(e)
            }
        )


@view_config(route_name='bedrock-agent-query', request_method='GET')
def bedrock_agent_info(request):
    """
    Get information about the Bedrock agent endpoint.
    
    GET /bedrock-agent/query
    """
    model_id = request.registry.settings.get(
        'bedrock.model_id',
        'anthropic.claude-3-5-sonnet-20241022-v2:0'
    )
    
    return {
        'endpoint': '/bedrock-agent/query',
        'method': 'POST',
        'description': 'Natural language query interface for PanKbase API',
        'model': model_id,
        'example': {
            'query': 'How many files are in analysis set PKBDS1349YHGQ?'
        },
        'supported_models': [
            'anthropic.claude-3-5-sonnet-20241022-v2:0',
            'anthropic.claude-3-opus-20240229-v1:0',
            'anthropic.claude-3-sonnet-20240229-v1:0',
            'anthropic.claude-3-haiku-20240307-v1:0',
        ]
    }
