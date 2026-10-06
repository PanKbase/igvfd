from snovault.elasticsearch.searches.configs import search_config


@search_config(
    name='Biosample'
)
def biosample():
    return {
        'facets': {
            # Defaults (shared)
            'type': {
                'title': 'Sample Type',
                'category': 'Sample',
                'description': 'Object type of the biosample.',
            },
            'sample_terms.term_name': {
                'title': 'Sample Term',
                'category': 'Sample',
                'description': 'Ontology term for the sample.',
            },
            'donors.diabetes_status_description': {
                'title': 'Donor Diabetes Status',
                'category': 'Donor',
                'description': 'Diabetes status of associated donors.',
            },
            'donors.age_group': {
                'title': 'Donor Age Group',
                'category': 'Donor',
                'description': 'Age group of associated donors.',
            },
            'status': {
                'title': 'Status',
                'category': 'Quality',
                'description': 'Release status of the sample.',
            },
            # Optional
            'classifications': {
                'title': 'Classifications',
                'category': 'Sample',
                'optional': True,
            },
            'virtual': {
                'title': 'Virtual',
                'category': 'Sample',
                'optional': True,
            },
            'file_sets.assay_term.term_name': {
                'title': 'Assay',
                'category': 'Sample',
                'optional': True,
            },
            'collections': {
                'title': 'Collection',
                'category': 'Provenance',
                'optional': True,
            },
            'lab.title': {
                'title': 'Lab',
                'category': 'Provenance',
                'optional': True,
            },
            'award.title': {
                'title': 'Award',
                'category': 'Provenance',
                'optional': True,
            },
            'release_timestamp': {
                'title': 'Release Date',
                'category': 'Provenance',
                'optional': True,
            },
            'creation_timestamp': {
                'title': 'Creation Date',
                'category': 'Provenance',
                'optional': True,
            },
            'audit.ERROR.category': {
                'title': 'Audit Category: Error',
                'category': 'Quality',
                'optional': True,
            },
            'audit.NOT_COMPLIANT.category': {
                'title': 'Audit Category: Not Compliant',
                'category': 'Quality',
                'optional': True,
            },
            'audit.WARNING.category': {
                'title': 'Audit Category: Warning',
                'category': 'Quality',
                'optional': True,
            },
            'audit.INTERNAL_ACTION.category': {
                'title': 'Audit Category: Internal Action',
                'category': 'Quality',
                'optional': True,
            },
        },
    }
