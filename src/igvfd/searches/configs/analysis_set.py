from snovault.elasticsearch.searches.configs import search_config


@search_config(
    name='AnalysisSet'
)
def analysis_set():
    return {
        'facets': {
            # Defaults (DE fields omitted until backfill ships)
            'annotation_category': {
                'title': 'Annotation Category',
                'category': 'Analysis Set Details',
                'description': 'High-level category derived from annotation type.',
            },
            'annotation_type': {
                'title': 'Annotation Type',
                'category': 'Analysis Set Details',
                'description': 'Type of analysis product represented by this analysis set.',
            },
            'file_set_type': {
                'title': 'File Set Type',
                'category': 'Analysis Set Details',
                'description': 'Level of this analysis set (intermediate, principal, or resource).',
            },
            'assay_titles': {
                'title': 'Assay Title',
                'category': 'Analysis Set Details',
                'description': 'Assay titles relevant to this analysis set.',
            },
            'samples.sample_terms.term_name': {
                'title': 'Sample Term',
                'category': 'Sample',
                'description': 'Sample ontology terms associated with the analysis set.',
            },
            'files.file_format': {
                'title': 'File Format',
                'category': 'File',
                'description': 'Format of files in the analysis set.',
            },
            'status': {
                'title': 'Status',
                'category': 'Quality',
                'description': 'Release status of the analysis set.',
            },
            # Optional — File
            'files.content_type': {
                'title': 'File Type',
                'category': 'File',
                'description': 'Content type of files in the analysis set.',
                'optional': True,
            },
            # Optional — Sample
            'donors.taxa': {
                'title': 'Taxa',
                'category': 'Sample',
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
            'input_file_sets': {
                'title': 'Input File Sets'
            },
            'summary': {
                'title': 'Summary'
            },
            'description': {
                'title': 'Description'
            },
            'donors.taxa': {
                'title': 'Taxa'
            },
            'file_set_type': {
                'title': 'File Set Type'
            },
            'annotation_type': {
                'title': 'Annotation Type'
            },
            'annotation_category': {
                'title': 'Annotation Category'
            },
            'cell_type': {
                'title': 'Cell Type'
            },
            'de_comparison_class': {
                'title': 'DE Comparison Class'
            },
            'de_method': {
                'title': 'DE Method'
            },
        },
    }
