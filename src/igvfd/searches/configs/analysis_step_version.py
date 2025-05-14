from snovault.elasticsearch.searches.configs import search_config


@search_config(
    name='AnalysisStepVersion'
)
def analysis_step_version():
    return {
        'facets': {
            'collections': {
                'title': 'Collections',
            },
            'award.component': {
                'title': 'Funding'
            },
            'status': {
                'title': 'Status'
            }
        },
        'facet_groups': [
            {
                'title': 'Provenance',
                'facet_fields': [
                    'collections',
                    'award.component',
                ],
            },
            {
                'title': 'Quality',
                'facet_fields': [
                    'status',
                ],
            },
        ],
        'columns': {
            'uuid': {
                'title': 'UUID'
            },
            'status': {
                'title': 'Status'
            },
            'title': {
                'title': 'Title'
            },
            'summary': {
                'title': 'Summary'
            }
        }
    }
