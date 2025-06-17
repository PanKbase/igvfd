from snovault.elasticsearch.searches.configs import search_config


@search_config(
    name='Workflow'
)
def workflow():
    return {
        'facets': {
            'collections': {
                'title': 'Collections',
            },
            'award.component': {
                'title': 'Award'
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
                    'collections',
                    'lab.title',
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
            'accession': {
                'title': 'Accession'
            },
            'alternate_accessions': {
                'title': 'Alternate Accessions'
            },
            'uuid': {
                'title': 'UUID'
            },
            'status': {
                'title': 'Status'
            },
            'name': {
                'title': 'Name'
            },
            'award': {
                'title': 'Award'
            },
            'summary': {
                'title': 'Summary'
            }
        }
    }
