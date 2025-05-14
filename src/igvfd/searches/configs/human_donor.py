from snovault.elasticsearch.searches.configs import search_config


@search_config(
    name='HumanDonor'
)
def human_donor():
    return {
        'facets': {
            'ethnicities': {
                'title': 'Ethnicities'
            },
            'gender': {
                'title': 'Gender'
            },
            'diabetes_status_description': {
                'title': 'Diabetes Status'
            },
            'aab_gada': {
                'title': 'AAB GADA POSITIVE'
            },
            'aab_ia2': {
                'title': 'AAB IA2 POSITIVE'
            },
            'aab_znt8': {
                'title': 'AAB ZNT8 POSITIVE'
            },
            'aab_iaa': {
                'title': 'AAB IAA POSITIVE'
            },
            'collections': {
                'title': 'Collections'
            },
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
                'title': 'Donor',
                'facet_fields': [
                    'ethnicities',
                    'gender',
                    'diabetes_status_description',
                    'aab_gada',
                    'aab_ia2',
                    'aab_iaa',
                    'aab_znt8',
                    'collections',
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
            'accession': {
                'title': 'Accession'
            },
            'alternate_accessions': {
                'title': 'Alternate Accessions'
            },
            'gender': {
                'title': 'Gender'
            },
            'award': {
                'title': 'Funding'
            },
            'ethnicities': {
                'title': 'Ethnicities'
            },
            'human_donor_identifiers': {
                'title': 'Human Donor Identifiers'
            },
            'status': {
                'title': 'Status'
            },
            'submitted_by': {
                'title': 'Submitted By'
            },
            'collections': {
                'title': 'Collections'
            },
            'phenotypic_features': {
                'title': 'Phenotypic Features'
            },
        }
    }
