from snovault.elasticsearch.searches.configs import search_config


@search_config(
    name='MeasurementSet'
)
def measurement_set():
    return {
        'facets': {
            # Defaults (Donor Diabetes Status omitted until donor embed expands)
            'assay_term.term_name': {
                'title': 'Assay',
                'category': 'Assay',
                'description': 'Assay ontology term for the measurement set.',
            },
            'preferred_assay_title': {
                'title': 'Preferred Assay Title',
                'category': 'Assay',
                'description': 'Preferred assay title for the measurement set.',
            },
            'samples.sample_terms.term_name': {
                'title': 'Sample Term',
                'category': 'Sample',
                'description': 'Sample ontology terms associated with the measurement set.',
            },
            'file_set_type': {
                'title': 'File Set Type',
                'category': 'Assay',
                'description': 'Category of this file set.',
            },
            'status': {
                'title': 'Status',
                'category': 'Quality',
                'description': 'Release status of the measurement set.',
            },
            # Optional — Sample
            'donors.taxa': {
                'title': 'Taxa',
                'category': 'Sample',
                'optional': True,
            },
            'samples.classifications': {
                'title': 'Classifications',
                'category': 'Sample',
                'optional': True,
            },
            'samples.targeted_sample_term.term_name': {
                'title': 'Targeted Sample Term',
                'category': 'Sample',
                'optional': True,
            },
            'samples.disease_terms.term_name': {
                'title': 'Disease Term',
                'category': 'Sample',
                'optional': True,
            },
            # Optional — Library / sequencing
            'library_construction_platform.term_name': {
                'title': 'Library Platform',
                'category': 'Library',
                'optional': True,
            },
            'sequencing_library_types': {
                'title': 'Library Material',
                'category': 'Library',
                'optional': True,
            },
            'files.sequencing_platform.term_name': {
                'title': 'Sequencing Platform',
                'category': 'Library',
                'optional': True,
            },
            'samples.modifications.modality': {
                'title': 'CRISPR Modality',
                'category': 'Assay',
                'optional': True,
            },
            'targeted_genes.symbol': {
                'title': 'Assay Targeted Genes',
                'category': 'Assay',
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
            'samples': {
                'title': 'Samples'
            },
            'donors': {
                'title': 'Donors'
            },
            'award': {
                'title': 'Award'
            },
            'lab': {
                'title': 'Lab'
            },
            'assay_term': {
                'title': 'Assay Term'
            },
            'preferred_assay_title': {
                'title': 'Preferred Assay Title'
            },
            'library_construction_platform': {
                'title': 'Library Construction Platform'
            },
            'sequencing_library_types': {
                'title': 'Sequencing Library Types'
            },
            'sequencing_chemistry': {
                'title': 'Sequencing Chemistry'
            },
            'targeted_genes.symbol': {
                'title': 'Assay Targeted Genes'
            },
            'protocols': {
                'title': 'Protocols'
            },
            'summary': {
                'title': 'Summary'
            },
            'donors.taxa': {
                'title': 'Taxa'
            },
            'file_set_type': {
                'title': 'File Set Type'
            },
        }
    }
