import pytest


def test_file_set_type_dependency(analysis_set_base, measurement_set, testapp):
    res = testapp.patch_json(
        analysis_set_base['@id'],
        {'file_set_type': 'principal analysis'}, expect_errors=True)
    assert res.status_code == 422
    res = testapp.patch_json(
        analysis_set_base['@id'],
        {'file_set_type': 'principal analysis',
         'input_file_sets': [measurement_set['@id']]})
    assert res.status_code == 200


def test_de_fields_valid_contrast(testapp, analysis_set_base):
    res = testapp.patch_json(
        analysis_set_base['@id'],
        {
            'annotation_type': 'differential_expression',
            'cell_type': 'beta',
            'de_comparison_class': 'disease_status',
            'de_contrast': 'T1D vs control',
            'de_method': 'pseudobulk_group_comparison',
        }
    )
    assert res.status_code == 200
    assert res.json['@graph'][0]['de_contrast'] == 'T1D vs control'
    assert res.json['@graph'][0]['cell_type'] == 'beta'


def test_de_fields_valid_trait(testapp, analysis_set_base):
    res = testapp.patch_json(
        analysis_set_base['@id'],
        {
            'annotation_type': 'differential_expression',
            'cell_type': 'alpha',
            'de_comparison_class': 'islet_function_trait',
            'de_trait': 'INSIEQ G 167 phase 2 AUC',
            'de_trait_description': 'Insulin secretion per IEQ, 16.7 mM glucose, second-phase AUC',
            'de_method': 'association',
        }
    )
    assert res.status_code == 200
    assert res.json['@graph'][0]['de_trait'] == 'INSIEQ G 167 phase 2 AUC'
    assert 'de_trait_description' in res.json['@graph'][0]


def test_de_fields_valid_cell_type_markers(testapp, analysis_set_base):
    res = testapp.patch_json(
        analysis_set_base['@id'],
        {
            'annotation_type': 'differential_expression',
            'cell_type': 'delta',
            'de_comparison_class': 'cell_type_markers',
            'de_contrast': 'delta vs all other cells',
            'de_method': 'one_vs_rest',
        }
    )
    assert res.status_code == 200
    assert res.json['@graph'][0]['de_comparison_class'] == 'cell_type_markers'


def test_cell_type_on_non_de_annotation(testapp, analysis_set_base):
    res = testapp.patch_json(
        analysis_set_base['@id'],
        {
            'annotation_type': 'chromatin_accessibility_peaks',
            'cell_type': 'beta',
        }
    )
    assert res.status_code == 200
    assert res.json['@graph'][0]['cell_type'] == 'beta'
    assert res.json['@graph'][0]['annotation_type'] == 'chromatin_accessibility_peaks'


def test_de_field_on_non_de_annotation_type(testapp, analysis_set_base):
    res = testapp.patch_json(
        analysis_set_base['@id'],
        {
            'annotation_type': 'sample_scrnaseq',
            'de_method': 'association',
        },
        expect_errors=True,
    )
    assert res.status_code == 422


def test_de_field_without_annotation_type(testapp, analysis_set_base):
    res = testapp.patch_json(
        analysis_set_base['@id'],
        {
            'de_comparison_class': 'disease_status',
            'de_contrast': 'T1D vs control',
        },
        expect_errors=True,
    )
    assert res.status_code == 422


def test_de_contrast_and_trait_mutually_exclusive(testapp, analysis_set_base):
    res = testapp.patch_json(
        analysis_set_base['@id'],
        {
            'annotation_type': 'differential_expression',
            'de_comparison_class': 'disease_status',
            'de_contrast': 'T1D vs control',
            'de_trait': 'BMI',
        },
        expect_errors=True,
    )
    assert res.status_code == 422


def test_de_trait_description_requires_de_trait(testapp, analysis_set_base):
    res = testapp.patch_json(
        analysis_set_base['@id'],
        {
            'annotation_type': 'differential_expression',
            'de_trait_description': 'Insulin secretion per IEQ, 16.7 mM glucose, second-phase AUC',
        },
        expect_errors=True,
    )
    assert res.status_code == 422


def test_de_bad_enum_value(testapp, analysis_set_base):
    res = testapp.patch_json(
        analysis_set_base['@id'],
        {
            'annotation_type': 'differential_expression',
            'cell_type': 'not_a_real_cell',
        },
        expect_errors=True,
    )
    assert res.status_code == 422


def test_de_contrast_requires_vs_pattern(testapp, analysis_set_base):
    res = testapp.patch_json(
        analysis_set_base['@id'],
        {
            'annotation_type': 'differential_expression',
            'de_comparison_class': 'disease_status',
            'de_contrast': 'T1D versus control',
        },
        expect_errors=True,
    )
    assert res.status_code == 422
