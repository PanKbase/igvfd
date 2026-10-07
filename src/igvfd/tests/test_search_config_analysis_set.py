from snovault.elasticsearch.searches.interfaces import SEARCH_CONFIG
from snovault import TYPES


def test_analysis_set_search_config_includes_de_facets_after_backfill(registry):
    """DE facets are default after the prod DE field backfill."""
    search_registry = registry[SEARCH_CONFIG]
    config = search_registry.get('AnalysisSet')
    for field in ('cell_type', 'de_comparison_class', 'de_method'):
        assert field in config.facets
        assert not config.facets[field].get('optional')
    for field in ('annotation_category', 'annotation_type', 'files.file_format'):
        assert field in config.facets
        assert not config.facets[field].get('optional')


def test_analysis_set_fuzzy_searchable_de_fields(registry):
    schema = registry[TYPES]['analysis_set'].schema
    fuzzy = schema.get('fuzzy_searchable_fields', [])
    for field in ('cell_type', 'de_contrast', 'de_trait', 'de_trait_description'):
        assert field in fuzzy
