import pytest


@pytest.fixture
def human_beta_cell_line(testapp, other_lab, award, human_donor, sample_term_pluripotent_stem_cell):
    item = {
        'award': award['@id'],
        'lab': other_lab['@id'],
        'sources': [other_lab['@id']],
        'donors': [human_donor['@id']],
        'sample_terms': [sample_term_pluripotent_stem_cell['@id']],
        'sample_name': 'EndoC-Bh1',
        'classifications': ['cell line'],
        'description': 'Human beta cell line derived from pancreatic islets'
    }
    return testapp.post_json('/human_beta_cell_line', item, status=201).json['@graph'][0]


@pytest.fixture
def human_beta_cell_line_with_passage_number(testapp, other_lab, award, human_donor, sample_term_pluripotent_stem_cell):
    item = {
        'award': award['@id'],
        'lab': other_lab['@id'],
        'sources': [other_lab['@id']],
        'donors': [human_donor['@id']],
        'sample_terms': [sample_term_pluripotent_stem_cell['@id']],
        'sample_name': 'EndoC-Bh2',
        'classifications': ['cell line'],
        'description': 'Human beta cell line with passage information',
        'passage_number': 15,
        'growth_medium': 'CMRL-1066 medium supplemented with 10% FBS'
    }
    return testapp.post_json('/human_beta_cell_line', item, status=201).json['@graph'][0]


@pytest.fixture
def human_beta_cell_line_with_authentication(testapp, other_lab, award, human_donor, sample_term_pluripotent_stem_cell):
    item = {
        'award': award['@id'],
        'lab': other_lab['@id'],
        'sources': [other_lab['@id']],
        'donors': [human_donor['@id']],
        'sample_terms': [sample_term_pluripotent_stem_cell['@id']],
        'sample_name': 'EndoC-Bh3',
        'classifications': ['cell line'],
        'description': 'Human beta cell line with authentication data',
        'authentication': 'STR profiling',
        'date_harvested': '2023-10-15'
    }
    return testapp.post_json('/human_beta_cell_line', item, status=201).json['@graph'][0]


@pytest.fixture
def human_beta_cell_line_v1(human_beta_cell_line):
    item = human_beta_cell_line.copy()
    item.update({
        'schema_version': '1'
    })
    return item