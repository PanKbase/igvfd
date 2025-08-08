from snovault.elasticsearch.searches.configs import search_config


@search_config(
    name='HumanBetaCellLine'
)
def human_beta_cell_line():
    return {
        'facets': {
            'sample_terms.term_name': {
                'title': 'Sample Terms',
            },
            'disease_terms.term_name': {
                'title': 'Disease Terms',
            },
            'treatments.treatment_term_name': {
                'title': 'Treatments',
            },
            'taxa': {
                'title': 'Taxa',
            },
            'sex': {
                'title': 'Sex'
            },
            'classifications': {
                'title': 'Classifications',
            },
            'collections': {
                'title': 'Collections',
            },
            'lab.title': {
                'title': 'Lab',
            },
            'award.component': {
                'title': 'Award',
            },
            'sources.title': {
                'title': 'Sources',
            },
            'status': {
                'title': 'Status'
            },
            'virtual': {
                'title': 'Virtual'
            },
            'file_sets.assay_term.term_name': {
                'title': 'Assay'
            },
            'biomarkers.classification': {
                'title': 'Biomarkers Classification'
            },
            'sample_name': {
                'title': 'Sample Name'
            },
            'passage_number': {
                'title': 'Passage Number'
            },
            'growth_medium': {
                'title': 'Growth Medium'
            },
            'authentication': {
                'title': 'Authentication'
            },
            'type': {
                'title': 'Object Type'
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
                'title': 'Cell Line',
                'facet_fields': [
                    'sample_terms.term_name',
                    'sample_name',
                    'classifications',
                    'passage_number',
                    'growth_medium',
                    'authentication',
                    'disease_terms.term_name',
                    'treatments.treatment_term_name',
                    'biomarkers.classification',
                    'virtual',
                ]
            },
            {
                'title': 'Sample',
                'facet_fields': [
                    'taxa',
                    'sex',
                    'file_sets.assay_term.term_name',
                ]
            },
            {
                'title': 'Provenance',
                'facet_fields': [
                    'collections',
                    'lab.title',
                    'award.component',
                    'sources.title',
                    'type',
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
            'passage_number': {
                'title': 'Passage Number'
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