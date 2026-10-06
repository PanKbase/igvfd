import pytest


pytestmark = [pytest.mark.indexing]


def test_analysis_set_de_facets_and_fuzzy_search(workbook, testapp):
    r = testapp.get('/search/?type=AnalysisSet&limit=0')
    facet_fields = {f['field'] for f in r.json.get('facets', [])}
    for field in ('cell_type', 'de_comparison_class', 'de_method'):
        assert field in facet_fields

    r = testapp.get('/search/?type=AnalysisSet&cell_type=beta')
    assert r.json['total'] >= 1
    assert any(item.get('cell_type') == 'beta' for item in r.json['@graph'])

    r = testapp.get('/search/?type=AnalysisSet&de_comparison_class=disease_status')
    assert r.json['total'] >= 1

    r = testapp.get('/search/?type=AnalysisSet&searchTerm=INSIEQ')
    assert r.json['total'] >= 1
    assert any(
        'INSIEQ' in (item.get('de_trait') or '')
        or 'INSIEQ' in (item.get('de_trait_description') or '')
        for item in r.json['@graph']
    )

    r = testapp.get('/search/?type=AnalysisSet&searchTerm=%22T1D%20vs%20control%22')
    assert r.json['total'] >= 1
    assert any(item.get('de_contrast') == 'T1D vs control' for item in r.json['@graph'])
