from snovault.elasticsearch.searches.configs import search_config


@search_config(
    name='HumanDonor'
)
def human_donor():
    return {
        'facets': {
            # Defaults (order = display order)
            'diabetes_status_description': {
                'title': 'Diabetes Status',
                'category': 'Clinical',
                'description': 'Reported diabetes status description for the donor.',
            },
            'derived_diabetes_status': {
                'title': 'HbA1c-derived Status',
                'category': 'Clinical',
                'description': 'Diabetes status derived from HbA1c when available.',
            },
            'age_group': {
                'title': 'Age Group',
                'category': 'Clinical',
                'description': 'Binned age group of the donor.',
            },
            'gender': {
                'title': 'Gender',
                'category': 'Clinical',
                'description': 'Reported gender of the donor.',
            },
            'aab_positive': {
                'title': 'Autoantibody Positive',
                'category': 'Clinical',
                'description': 'Whether the donor is positive for any autoantibody.',
            },
            'donation_type': {
                'title': 'Donation Type',
                'category': 'Clinical',
                'description': 'Type of donation associated with the donor.',
            },
            'status': {
                'title': 'Status',
                'category': 'Quality',
                'description': 'Release status of the donor object.',
            },
            # Optional — Clinical
            't1d_stage': {
                'title': 'T1D Stage',
                'category': 'Clinical',
                'description': 'Type 1 diabetes stage when derivable.',
                'optional': True,
            },
            'aab_count': {
                'title': 'Autoantibody Count',
                'category': 'Clinical',
                'description': 'Number of autoantibodies positive.',
                'optional': True,
            },
            'family_history_of_diabetes': {
                'title': 'Family History of Diabetes',
                'category': 'Clinical',
                'description': 'Family history of diabetes.',
                'optional': True,
            },
            'label_hba1c_discordant': {
                'title': 'Label vs HbA1c Discordant',
                'category': 'Clinical',
                'description': 'Whether reported diabetes status disagrees with HbA1c-derived status.',
                'optional': True,
            },
            'aab_gada': {
                'title': 'AAB GADA Positive',
                'category': 'Clinical',
                'description': 'GADA autoantibody status.',
                'optional': True,
            },
            'aab_ia2': {
                'title': 'AAB IA2 Positive',
                'category': 'Clinical',
                'description': 'IA-2 autoantibody status.',
                'optional': True,
            },
            'aab_iaa': {
                'title': 'AAB IAA Positive',
                'category': 'Clinical',
                'description': 'IAA autoantibody status.',
                'optional': True,
            },
            'aab_znt8': {
                'title': 'AAB ZnT8 Positive',
                'category': 'Clinical',
                'description': 'ZnT8 autoantibody status.',
                'optional': True,
            },
            'data_available_datasets': {
                'title': 'Data Available',
                'category': 'Clinical',
                'description': 'Normalized dataset types available for this donor.',
                'optional': True,
            },
            # Optional — Genetics
            'genetic_sex': {
                'title': 'Genetic Sex',
                'category': 'Genetics',
                'description': 'Genetically determined sex.',
                'optional': True,
            },
            'dominant_genetic_ancestry': {
                'title': 'Genetic Ancestry',
                'category': 'Genetics',
                'description': 'Dominant genetic ancestry.',
                'optional': True,
            },
            'ethnicities': {
                'title': 'Self-reported Ethnicity',
                'category': 'Genetics',
                'description': 'Self-reported ethnicity.',
                'optional': True,
            },
            'sex_discordant': {
                'title': 'Sex Discordant',
                'category': 'Genetics',
                'description': 'Whether reported gender and genetic sex disagree.',
                'optional': True,
            },
            # Optional — Tissue
            'pancreas_tissue_available': {
                'title': 'Pancreas Tissue Available',
                'category': 'Tissue',
                'description': 'Whether pancreas tissue is available.',
                'optional': True,
            },
            'other_tissues_available': {
                'title': 'Other Tissues Available',
                'category': 'Tissue',
                'description': 'Whether other tissues are available.',
                'optional': True,
            },
            'data_available_tissues': {
                'title': 'Data Available Tissues',
                'category': 'Tissue',
                'description': 'Tissues with associated data.',
                'optional': True,
            },
            # Optional — Quality
            'tier1_complete': {
                'title': 'Tier 1 Complete',
                'category': 'Quality',
                'description': 'Whether tier 1 metadata is complete.',
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
                'title': 'Award'
            },
            'lab': {
                'title': 'Lab'
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
            'phenotypic_features': {
                'title': 'Phenotypic Features'
            },
            'diabetes_status_description': {
                'title': 'Diabetes Status'
            },
            'derived_diabetes_status': {
                'title': 'HbA1c-derived Status'
            },
            'age_group': {
                'title': 'Age Group'
            },
        }
    }
