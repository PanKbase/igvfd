"""Search config facet metadata for optional/default facet UX."""

from snovault.elasticsearch.searches.interfaces import SEARCH_CONFIG


OPTIONAL_FACET_TYPES = [
    'HumanDonor',
    'PrimaryIslet',
    'PrimaryCell',
    'HumanBetaCellLines',
    'Biosample',
    'AnalysisSet',
    'MeasurementSet',
]


def _facets(registry, name):
    return registry[SEARCH_CONFIG].get(name).facets


def test_search_configs_have_optional_and_category(registry):
    """Every configured type exposes category; optional facets are marked."""
    search_registry = registry[SEARCH_CONFIG]
    for name in OPTIONAL_FACET_TYPES:
        facets = search_registry.get(name).facets
        assert facets, f'{name} has no facets'
        optional_count = 0
        for field, config in facets.items():
            assert 'title' in config, f'{name}.{field} missing title'
            assert 'category' in config, f'{name}.{field} missing category'
            if config.get('optional'):
                optional_count += 1
        assert optional_count > 0, f'{name} has no optional facets'


def test_human_donor_default_facets(registry):
    facets = _facets(registry, 'HumanDonor')
    defaults = [f for f, c in facets.items() if not c.get('optional')]
    assert 'diabetes_status_description' in defaults
    assert 'derived_diabetes_status' in defaults
    assert 'age_group' in defaults
    assert 'gender' in defaults
    assert 'aab_positive' in defaults
    assert 'donation_type' in defaults
    assert 'status' in defaults
    # Gate 1: these must be optional, not default
    assert facets['t1d_stage'].get('optional') is True
    assert facets['data_available_datasets'].get('optional') is True
    # Provenance optional filters removed
    assert 'collections' not in facets
    assert 'lab.title' not in facets
    assert 'award.title' not in facets
    assert 'award.component' not in facets
    assert 'release_timestamp' not in facets
    assert 'creation_timestamp' not in facets
    assert 'type' not in facets


def test_analysis_set_defaults_omit_de_fields(registry):
    facets = _facets(registry, 'AnalysisSet')
    for field in ('cell_type', 'de_comparison_class', 'de_method'):
        assert field not in facets
    defaults = [f for f, c in facets.items() if not c.get('optional')]
    assert defaults == [
        'annotation_category',
        'annotation_type',
        'file_set_type',
        'assay_titles',
        'samples.sample_terms.term_name',
        'files.file_format',
        'status',
    ]
    assert facets['files.content_type'].get('optional') is True
    assert 'collections' not in facets
    assert 'lab.title' not in facets
    assert 'award.title' not in facets
    assert 'award.component' not in facets
    assert 'release_timestamp' not in facets
    assert 'creation_timestamp' not in facets
    assert 'type' not in facets


def test_measurement_set_defaults(registry):
    facets = _facets(registry, 'MeasurementSet')
    defaults = [f for f, c in facets.items() if not c.get('optional')]
    assert defaults == [
        'assay_term.term_name',
        'preferred_assay_title',
        'samples.sample_terms.term_name',
        'file_set_type',
        'status',
    ]
    assert 'donors.diabetes_status_description' not in facets
    assert 'lab.title' not in facets
    assert 'award.title' not in facets
    assert 'collections' not in facets
    assert 'type' not in facets


def test_primary_islet_defaults(registry):
    facets = _facets(registry, 'PrimaryIslet')
    defaults = [f for f, c in facets.items() if not c.get('optional')]
    assert 'isolation_center' in defaults
    assert 'islet_function_available' in defaults
    assert 'organ_source' in defaults
    assert 'sample_terms.term_name' in defaults
    assert 'donors.diabetes_status_description' in defaults
    assert 'status' in defaults
    assert 'collections' not in facets
    assert 'lab.title' not in facets
    assert 'award.title' not in facets
    assert facets['preservation_method'].get('optional') is True
    assert facets['hand_picked'].get('optional') is True
    assert 'purity' not in facets
    assert 'treatments.treatment_term_name' not in facets


def test_human_beta_cell_line_defaults(registry):
    facets = _facets(registry, 'HumanBetaCellLines')
    defaults = [f for f, c in facets.items() if not c.get('optional')]
    assert 'sample_name.raw' in defaults
    assert 'excision_status' in defaults
    assert 'sample_terms.term_name' in defaults
    assert 'status' in defaults


def test_no_facet_groups(registry):
    """Tabbed facet_groups are removed in favor of optional/category."""
    search_registry = registry[SEARCH_CONFIG]
    as_dict = search_registry.as_dict()
    for name in OPTIONAL_FACET_TYPES:
        groups = as_dict[name].get('facet_groups')
        assert not groups, f'{name} still has facet_groups: {groups}'


def test_audits_are_optional(registry):
    search_registry = registry[SEARCH_CONFIG]
    for name in OPTIONAL_FACET_TYPES:
        facets = search_registry.get(name).facets
        for field, config in facets.items():
            if field.startswith('audit.'):
                assert config.get('optional') is True, f'{name}.{field} must be optional'
