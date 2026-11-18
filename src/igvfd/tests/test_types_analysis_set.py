import pytest


def test_calculated_donors(testapp, analysis_set_base, primary_cell, human_donor, in_vitro_cell_line, rodent_donor):
    testapp.patch_json(
        analysis_set_base['@id'],
        {
            'samples': [primary_cell['@id']]
        }
    )
    res = testapp.get(analysis_set_base['@id'])
    assert set([donor['@id'] for donor in res.json.get('donors')]) == {human_donor['@id']}
    testapp.patch_json(
        analysis_set_base['@id'],
        {
            'samples': [in_vitro_cell_line['@id']]
        }
    )
    res = testapp.get(analysis_set_base['@id'])
    assert set([donor['@id'] for donor in res.json.get('donors')]) == {rodent_donor['@id']}


def test_assay_titles(testapp, analysis_set_base, measurement_set_mpra, measurement_set_multiome):
    testapp.patch_json(
        analysis_set_base['@id'],
        {
            'input_file_sets': [measurement_set_mpra['@id']]
        }
    )
    res = testapp.get(analysis_set_base['@id'])
    assert set(res.json.get('assay_titles')) == {'massively parallel reporter assay'}
    testapp.patch_json(
        measurement_set_mpra['@id'],
        {
            'preferred_assay_title': 'lentiMPRA'
        }
    )
    res = testapp.get(analysis_set_base['@id'])
    assert set(res.json.get('assay_titles')) == {'lentiMPRA'}
    testapp.patch_json(
        analysis_set_base['@id'],
        {
            'input_file_sets': [measurement_set_mpra['@id'],
                                measurement_set_multiome['@id']]
        }
    )
    res = testapp.get(analysis_set_base['@id'])
    assert set(res.json.get('assay_titles')) == {'ATAC-seq', 'lentiMPRA'}


def test_analysis_set_summary(testapp, analysis_set_base, base_auxiliary_set, measurement_set_mpra, measurement_set_multiome, principal_analysis_set):
    # With no input_file_sets present, summary is based on analysis file_set_type only
    res = testapp.get(analysis_set_base['@id']).json
    assert res.get('summary', '') == 'intermediate analysis of data'
    # When no MeasurementSets (even nested in AnalysisSets) are present, data for other FileSet types are included in the summary
    testapp.patch_json(
        analysis_set_base['@id'],
        {
            'input_file_sets': [base_auxiliary_set['@id']]
        }
    )
    res = testapp.get(analysis_set_base['@id']).json
    assert res.get('summary', '') == 'intermediate analysis of gRNA sequencing data'
    testapp.patch_json(
        analysis_set_base['@id'],
        {
            'input_file_sets': [base_auxiliary_set['@id'],
                                measurement_set_mpra['@id'],
                                measurement_set_multiome['@id']]
        }
    )
    res = testapp.get(analysis_set_base['@id']).json
    assert res.get('summary', '') == 'intermediate analysis of ATAC-seq, massively parallel reporter assay data'
    # Preferred_assay_title of MeasurementSet is used instead of assay_term in summary whenever present
    testapp.patch_json(
        measurement_set_mpra['@id'],
        {
            'preferred_assay_title': 'lentiMPRA'
        }
    )
    testapp.patch_json(
        analysis_set_base['@id'],
        {
            'input_file_sets': [measurement_set_mpra['@id'],
                                measurement_set_multiome['@id'],
                                principal_analysis_set['@id']]
        }
    )
    res = testapp.get(analysis_set_base['@id']).json
    assert res.get('summary', '') == 'intermediate analysis of ATAC-seq, STARR-seq, lentiMPRA data'


def test_annotation_category(testapp, analysis_set_base, measurement_set):
    # No annotation_type -> no annotation_category
    res = testapp.get(analysis_set_base['@id']).json
    assert 'annotation_category' not in res

    # Direct mapping from annotation_type
    testapp.patch_json(
        analysis_set_base['@id'],
        {'annotation_type': 'sample_scrnaseq'}
    )
    res = testapp.get(analysis_set_base['@id']).json
    assert res['annotation_type'] == 'sample_scrnaseq'
    assert res['annotation_category'] == 'Gene expression'

    testapp.patch_json(
        analysis_set_base['@id'],
        {'annotation_type': 'chromatin_accessibility_peaks'}
    )
    res = testapp.get(analysis_set_base['@id']).json
    assert res['annotation_category'] == 'Chromatin accessibility'

    testapp.patch_json(
        analysis_set_base['@id'],
        {'annotation_type': 'differential_expression'}
    )
    res = testapp.get(analysis_set_base['@id']).json
    assert res['annotation_category'] == 'Differential expression'

    testapp.patch_json(
        analysis_set_base['@id'],
        {'annotation_type': 'islet_function_perifusion'}
    )
    res = testapp.get(analysis_set_base['@id']).json
    assert res['annotation_category'] == 'Islet function'

    testapp.patch_json(
        analysis_set_base['@id'],
        {'annotation_type': 'metadata_table'}
    )
    res = testapp.get(analysis_set_base['@id']).json
    assert res['annotation_category'] == 'Resource'

    testapp.patch_json(
        analysis_set_base['@id'],
        {'annotation_type': 'qtl_colocalization'}
    )
    res = testapp.get(analysis_set_base['@id']).json
    assert res['annotation_category'] == 'QTL and fine-mapping'

    testapp.patch_json(
        analysis_set_base['@id'],
        {'annotation_type': 'unclear'}
    )
    res = testapp.get(analysis_set_base['@id']).json
    assert res['annotation_category'] == 'Unclear'

    # reference_atlas depends on assay title
    testapp.patch_json(
        analysis_set_base['@id'],
        {
            'annotation_type': 'reference_atlas',
            'input_file_sets': [measurement_set['@id']],
        }
    )
    res = testapp.get(analysis_set_base['@id']).json
    # measurement_set has preferred_assay_title STARR-seq by default in some fixtures,
    # or assay term name — neither is scRNA-seq/snATAC-seq, so Unclear.
    assert res['annotation_category'] == 'Unclear'

    testapp.patch_json(
        measurement_set['@id'],
        {'preferred_assay_title': 'scRNA-seq'}
    )
    res = testapp.get(analysis_set_base['@id']).json
    assert res['annotation_category'] == 'Gene expression'

    testapp.patch_json(
        measurement_set['@id'],
        {'preferred_assay_title': 'snATAC-seq'}
    )
    res = testapp.get(analysis_set_base['@id']).json
    assert res['annotation_category'] == 'Chromatin accessibility'


def test_annotation_type_enum(testapp, analysis_set_base):
    res = testapp.patch_json(
        analysis_set_base['@id'],
        {'annotation_type': 'not_a_real_type'},
        expect_errors=True,
    )
    assert res.status_code == 422


def test_analysis_set_workflows_empty_without_step_versions(testapp, analysis_set_base, analysis_set_with_sample, tabular_file):
    # No files at all
    res = testapp.get(analysis_set_base['@id']).json
    assert res.get('workflows') == []
    # Has a file, but the file has no analysis_step_version
    res = testapp.get(analysis_set_with_sample['@id']).json
    assert res.get('workflows') == []


def test_analysis_set_workflows_from_files(testapp, analysis_set_with_sample, tabular_file, analysis_step_version, base_workflow, lab, award):
    testapp.patch_json(
        tabular_file['@id'],
        {
            'analysis_step_version': analysis_step_version['@id']
        }
    )
    # A second file from the same workflow is reported once
    testapp.post_json(
        '/tabular_file',
        {
            'award': award['@id'],
            'lab': lab['@id'],
            'md5sum': 'fb2ab5dbb7a8f0bb0b6d29a6bb3ab7a5',
            'file_format': 'tsv',
            'file_set': analysis_set_with_sample['@id'],
            'content_type': 'peaks',
            'controlled_access': False,
            'analysis_step_version': analysis_step_version['@id']
        },
        status=201
    )
    res = testapp.get(analysis_set_with_sample['@id']).json
    assert [workflow['@id'] for workflow in res.get('workflows')] == [base_workflow['@id']]
    assert res['workflows'][0]['accession'] == base_workflow['accession']
    assert res['workflows'][0]['name'] == base_workflow['name']
    res = testapp.get(analysis_set_with_sample['@id'] + '@@object').json
    assert res.get('workflows') == [base_workflow['@id']]
