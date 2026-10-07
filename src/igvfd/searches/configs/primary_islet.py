from snovault.elasticsearch.searches.configs import search_config


@search_config(
    name='PrimaryIslet'
)
def primary_islet():
    return {
        'facets': {
            # Defaults
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
            'isolation_center': {
                'title': 'Isolation Center',
                'category': 'Islet prep',
                'description': 'Center that isolated the islet preparation.',
            },
            'islet_function_available': {
                'title': 'Islet Function Available',
                'category': 'Islet prep',
                'description': 'Whether islet function (perifusion) data is available.',
            },
            'organ_source': {
                'title': 'Organ Source',
                'category': 'Islet prep',
                'description': 'Source of the organ used for the islet preparation.',
            },
            'status': {
                'title': 'Status',
                'category': 'Quality',
                'description': 'Release status of the sample.',
            },
            # Optional — Islet prep
            'preservation_method': {
                'title': 'Preservation Method',
                'category': 'Islet prep',
                'description': 'Tissue preservation method.',
                'optional': True,
            },
            'hand_picked': {
                'title': 'Hand Picked',
                'category': 'Islet prep',
                'description': 'Whether islets were hand picked.',
                'optional': True,
            },
            # Optional — Donor
            'donors.gender': {
                'title': 'Donor Gender',
                'category': 'Donor',
                'description': 'Gender of associated donors.',
                'optional': True,
            },
            'donors.t1d_stage': {
                'title': 'Donor T1D Stage',
                'category': 'Donor',
                'description': 'T1D stage of associated donors.',
                'optional': True,
            },
            'donors.aab_positive': {
                'title': 'Donor Autoantibody Positive',
                'category': 'Donor',
                'description': 'Whether associated donors are autoantibody positive.',
                'optional': True,
            },
            # Optional — Sample misc
            'sex': {
                'title': 'Sex',
                'category': 'Sample',
                'optional': True,
            },
            'classifications': {
                'title': 'Classifications',
                'category': 'Sample',
                'optional': True,
            },
            'taxa': {
                'title': 'Taxa',
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
            # Optional — Provenance
            'sources.title': {
                'title': 'Sources',
                'category': 'Provenance',
                'optional': True,
            },
            # Optional — Quality
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
            'sample_terms': {
                'title': 'Sample Terms'
            },
            'alternate_accessions': {
                'title': 'Alternate Accessions'
            },
            'classifications': {
                'title': 'Classifications'
            },
            'donors': {
                'title': 'Donors'
            },
            'date_obtained': {
                'title': 'Date Obtained'
            },
            'taxa': {
                'title': 'Taxa'
            },
            'award': {
                'title': 'Award'
            },
            'lab': {
                'title': 'Lab'
            },
            'status': {
                'title': 'Status'
            },
            'summary': {
                'title': 'Summary'
            },
            'virtual': {
                'title': 'Virtual'
            },
            'description': {
                'title': 'Description'
            }
        }
    }
