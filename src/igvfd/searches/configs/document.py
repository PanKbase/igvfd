from snovault.elasticsearch.searches.configs import search_config


@search_config(
    name='Document'
)
def document():
    return {
        'facets': {
            'document_type': {
                'title': 'Document Type'
            },
            'characterization_method': {
                'title': 'Characterization Method'
            },
            'award.component': {
                'title': 'Funding',
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
                'title': 'Document',
                'facet_fields': [
                    'document_type',
                    'characterization_method',
                ]
            },
            {
                'title': 'Provenance',
                'facet_fields': [
                    'award.component',
                ]
            },
            {
                'title': 'Quality',
                'facet_fields': [
                    'status',
                    'audit.ERROR.category',
                    'audit.NOT_COMPLIANT.category',
                    'audit.WARNING.category',
                    'audit.INTERNAL_ACTION.category',
                ]
            },
        ],
        'columns': {
            'uuid': {
                'title': 'UUID'
            },
            'description': {
                'title': 'Description'
            },
            'award': {
                'title': 'Funding'
            },
            'document_type': {
                'title': 'Document Type'
            },
            'status': {
                'title': 'Status'
            },
            'submitted_by': {
                'title': 'Submitted By'
            },
            'attachment': {
                'title': 'Attachment'
            },
        }
    }
