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
            'data_available_datasets': {
                'title': 'Data Available Datasets'
            },
            'data_available_tissues': {
                'title': 'Data Available Tissues'
            },
            'age_group': {
                'title': 'Age Group'
            },
            'aab_count': {
                'title': 'Autoantibody Count'
            },
            'aab_positive': {
                'title': 'Autoantibody Positive'
            },
            'donation_type': {
                'title': 'Donation Type'
            },
            'genetic_sex': {
                'title': 'Genetic Sex'
            },
            'family_history_of_diabetes': {
                'title': 'Family History of Diabetes'
            },
            'sex_discordant': {
                'title': 'Sex Discordant'
            },
            'label_hba1c_discordant': {
                'title': 'Label vs HbA1c Discordant'
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
                    'genetic_sex',
                    'diabetes_status_description',
                    'donation_type',
                    'age_group',
                    'aab_gada',
                    'aab_ia2',
                    'aab_iaa',
                    'aab_znt8',
                    'aab_count',
                    'aab_positive',
                    'data_available_datasets',
                    'data_available_tissues',
                    'family_history_of_diabetes',
                    'sex_discordant',
                    'label_hba1c_discordant',
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
