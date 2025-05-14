from snovault.elasticsearch.searches.configs import search_config


@search_config(
    name='InstitutionalCertificate'
)
def institutional_certificate():
    return {
        'facets': {
            'award.component': {
                'title': 'Funding'
            },
            'status': {
                'title': 'Status'
            },
            'audit.ERROR.category': {
                'title': 'Audit Category: Error'
            },
            'audit.NOT_COMPLIANT.category': {
                'title': 'Audit Category: Not Compliant'
            },
            'audit.WARNING.category': {
                'title': 'Audit Category: Warning'
            },
            'audit.INTERNAL_ACTION.category': {
                'title': 'Audit Category: Internal Action'
            },
        },
        'facet_groups': [
            {
                'title': 'Provenance',
                'facet_fields': [
                    'award.component',
                ],
            },
            {
                'title': 'Quality',
                'facet_fields': [
                    'status',
                    'audit.ERROR.category',
                    'audit.NOT_COMPLIANT.category',
                    'audit.WARNING.category',
                    'audit.INTERNAL_ACTION.category',
                ],
            },
        ],
        'columns': {
            'certificate_identifier': {
                'title': 'Certificate Identifier'
            },
            'urls': {
                'title': 'URL'
            },
            'uuid': {
                'title': 'UUID'
            },
            'status': {
                'title': 'Status'
            },
            'award': {
                'title': 'Funding'
            },
            'summary': {
                'title': 'Summary'
            }
        }
    }
