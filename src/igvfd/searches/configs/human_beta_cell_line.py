from snovault.elasticsearch.searches.configs import search_config


@search_config(
    name='HumanBetaCellLines'
)
def human_beta_cell_line():
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
            'sample_name.raw': {
                'title': 'Sample Name',
                'category': 'Cell line',
                'description': 'Name of the cell line sample.',
            },
            'excision_status': {
                'title': 'Excision Status',
                'category': 'Cell line',
                'description': 'Status of immortalization cassette excision.',
            },
            'status': {
                'title': 'Status',
                'category': 'Quality',
                'description': 'Release status of the sample.',
            },
            # Optional — Cell line
            'growth_medium.raw': {
                'title': 'Growth Medium',
                'category': 'Cell line',
                'optional': True,
            },
            'authentication.raw': {
                'title': 'Authentication',
                'category': 'Cell line',
                'optional': True,
            },
            # Optional — Donor
            'donors.gender': {
                'title': 'Donor Gender',
                'category': 'Donor',
                'optional': True,
            },
            'donors.t1d_stage': {
                'title': 'Donor T1D Stage',
                'category': 'Donor',
                'optional': True,
            },
            'donors.aab_positive': {
                'title': 'Donor Autoantibody Positive',
                'category': 'Donor',
                'optional': True,
            },
            'gender': {
                'title': 'Gender',
                'category': 'Sample',
                'optional': True,
            },
            # Optional — Sample
            'disease_terms.term_name': {
                'title': 'Disease Terms',
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
            'biomarkers.classification': {
                'title': 'Biomarkers Classification',
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
            'sample_name': {
                'title': 'Sample Name'
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
            'growth_medium': {
                'title': 'Growth Medium'
            },
            'date_obtained': {
                'title': 'Date Obtained'
            },
            'date_harvested': {
                'title': 'Date Harvested'
            },
            'authentication': {
                'title': 'Authentication'
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
