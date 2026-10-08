"""Unit tests for HumanDonor / PrimaryIslet calculated helpers (no Pyramid)."""

from igvfd.calculated.human_donor import donor_calc_bundle
from igvfd.calculated.primary_islet import islet_calc_bundle


def test_data_available_multiome_expansion():
    props = {
        'data_available': [
            {'dataset': 'scMultiome', 'dataset_tissue': 'Islet'},
            {'dataset': 'snATAC-seq', 'dataset_tissue': '-'},
        ]
    }
    calc = donor_calc_bundle(props)
    assert 'scMultiome|Islet' in calc['data_available_keys']
    assert 'snATACseq|Islet' in calc['data_available_keys']
    assert 'scRNAseq|Islet' in calc['data_available_keys']
    assert 'snATACseq|unspecified' in calc['data_available_keys']
    assert 'snATACseq' in calc['data_available_datasets']
    assert 'scRNAseq' in calc['data_available_datasets']
    assert 'unspecified' in calc['data_available_tissues']


def test_aab_omit_when_untested_and_count_when_tested():
    assert 'aab_count' not in donor_calc_bundle({'age': 40})
    tested_neg = donor_calc_bundle({'aab_gada': False, 'aab_ia2': False})
    assert tested_neg['aab_count'] == 0
    assert tested_neg['aab_positive'] is False
    assert tested_neg['aab_summary'] == 'none positive'
    tested_pos = donor_calc_bundle({'aab_gada': True, 'aab_ia2': True, 'aab_iaa': False})
    assert tested_pos['aab_count'] == 2
    assert tested_pos['aab_positive'] is True
    assert tested_pos['aab_summary'] == 'GADA+, IA2+'


def test_age_group_and_pediatric():
    assert donor_calc_bundle({'age': 10})['age_group'] == '0-12'
    assert donor_calc_bundle({'age': 15})['pediatric'] is True
    assert donor_calc_bundle({'age': 40})['age_group'] == '40-64'
    assert donor_calc_bundle({'age': 70})['age_group'] == '65+'


def test_discordance_flags():
    sex = donor_calc_bundle({'gender': 'Male', 'genetic_sex': 'Female'})
    assert sex['sex_discordant'] is True
    assert 'sex_discordant' not in donor_calc_bundle({'gender': 'Male', 'genetic_sex': '-'})
    label = donor_calc_bundle({
        'diabetes_status_description': 'Control Without Diabetes',
        'derived_diabetes_status': 'Diabetes',
    })
    assert label['label_hba1c_discordant'] is True
    ok = donor_calc_bundle({
        'diabetes_status_description': 'Type 2 Diabetes',
        'derived_diabetes_status': 'Diabetes',
    })
    assert ok.get('label_hba1c_discordant') is False


def test_ancestry_and_grs_and_tier1():
    ancestry = donor_calc_bundle({
        'genetic_ethnicities': [
            {'ethnicity': 'European', 'percentage': 40},
            {'ethnicity': 'African', 'percentage': 60},
        ]
    })
    assert ancestry['dominant_genetic_ancestry'] == 'African'
    single = donor_calc_bundle({'genetic_ethnicities': [{'ethnicity': 'European'}]})
    assert single['dominant_genetic_ancestry'] == 'European'
    grs = donor_calc_bundle({
        'genetic_risk_score': [
            {'method': 'GRS2', 'overall_score': 10.5, 'normalized_score': 0.5},
            {'method': 'T2D_GRS_Mahajan', 'overall_score': 21.0, 'normalized_score': 0.6},
        ]
    })
    assert grs['grs2_score'] == 10.5
    assert grs['t2d_grs_normalized'] == 0.6
    incomplete = donor_calc_bundle({'age': 40, 'lab': '/labs/x/'})
    assert incomplete['tier1_complete'] is False
    complete = donor_calc_bundle({
        'age': 40,
        'center_donor_id': 'HPAP-1',
        'lab': '/labs/x/',
        'living_donor': False,
        'taxa': 'Homo sapiens',
        'gender': 'Female',
        'bmi': 25,
        'diabetes_status': ['/phenotype-terms/x/'],
        'diabetes_status_description': 'Type 1 Diabetes',
    })
    assert complete['tier1_complete'] is True


def test_islet_purity_and_viability():
    assert islet_calc_bundle({'purity': ['10', '25.5', 'n/a']})['purity_value'] == 25.5
    assert 'purity_value' not in islet_calc_bundle({'purity': ['bad']})
    assert islet_calc_bundle({
        'post_shipment_viability_quantitative': 90,
        'post_shipment_islet_viability': 80,
    })['post_shipment_viability'] == 90
    assert islet_calc_bundle({
        'post_shipment_islet_viability': 80,
    })['post_shipment_viability'] == 80
