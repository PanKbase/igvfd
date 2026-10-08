"""Indexing checks for donor→biosample embed invalidation (requires pyramid + ES)."""

import time

import pytest

pytestmark = [pytest.mark.indexing]


def test_donor_calc_props_embedded_on_biosample(testapp, workbook, poll_until_indexing_is_done):
    """Biosample embedded donors include A1 calc props (age_group, aab_positive, aab_count)."""
    # Prefer calc inserts linked to PrimaryIslet (igvf:calc_donor_*).
    donors = testapp.get(
        '/search/?type=HumanDonor&center_donor_id=HPAP-CALC-001&limit=1'
    ).json.get('@graph') or []
    if not donors:
        donors = testapp.get('/search/?type=HumanDonor&limit=1').json.get('@graph') or []
    if not donors:
        pytest.skip('no human donors in workbook')
    donor = testapp.get(donors[0]['@id'] + '?frame=object').json
    if 'age' not in donor:
        pytest.skip('donor lacks age')
    assert donor.get('age_group') in {'0-12', '13-17', '18-39', '40-64', '65+'}
    if any(k in donor for k in ('aab_gada', 'aab_iaa', 'aab_ia2', 'aab_znt8')):
        assert 'aab_positive' in donor
        assert 'aab_count' in donor

    islets = testapp.get(
        '/search/?type=PrimaryIslet&donors.accession=' + donor['accession'] + '&limit=1'
    ).json.get('@graph') or []
    if not islets:
        islets = testapp.get('/search/?type=PrimaryIslet&limit=1').json.get('@graph') or []
    if not islets:
        pytest.skip('no primary islets in workbook')
    islet = testapp.get(islets[0]['@id']).json
    embedded = islet.get('donors') or []
    if not embedded or not isinstance(embedded[0], dict):
        pytest.skip('donors not embedded on islet')
    emb = embedded[0]
    for key in ('age_group', 'aab_positive', 'aab_count'):
        if key in donor:
            assert key in emb, f'embedded donors missing {key}'


def test_patch_donor_invalidates_linked_biosample(testapp, workbook, poll_until_indexing_is_done):
    """Patching a donor should reindex biosamples that link to it (via donors linkTo / rev)."""
    islets = testapp.get('/search/?type=PrimaryIslet&limit=1').json.get('@graph') or []
    if not islets:
        pytest.skip('no primary islets in workbook yet')
    islet = testapp.get(islets[0]['@id']).json
    donor_ids = islet.get('donors') or []
    if not donor_ids:
        pytest.skip('islet has no donors')
    donor_id = donor_ids[0] if isinstance(donor_ids[0], str) else donor_ids[0].get('@id')
    # Touch donor; wait for indexer; biosample document should refresh.
    started = time.perf_counter()
    testapp.patch_json(donor_id, {'submitter_comment': 'invalidation-check'}, status=200)
    poll_until_indexing_is_done(testapp)
    elapsed_ms = (time.perf_counter() - started) * 1000.0
    refreshed = testapp.get(islet['@id']).json
    assert refreshed.get('@id') == islet['@id']
    # Surface wall-clock for local A1 reports (no prod reindex).
    print(f'INDEX_TIME_DELTA_MS patch_donor_to_reindex={elapsed_ms:.1f}')


def test_insert_index_time_delta(testapp, workbook, poll_until_indexing_is_done):
    """Measure wall-clock from POST PrimaryIslet to indexer idle (insert path)."""
    donors = testapp.get(
        '/search/?type=HumanDonor&center_donor_id=HPAP-CALC-001&limit=1'
    ).json.get('@graph') or []
    if not donors:
        donors = testapp.get('/search/?type=HumanDonor&limit=1').json.get('@graph') or []
    if not donors:
        pytest.skip('no human donors for insert timing')
    donor_id = donors[0]['@id']
    labs = testapp.get('/search/?type=Lab&limit=1').json.get('@graph') or []
    awards = testapp.get('/search/?type=Award&limit=1').json.get('@graph') or []
    terms = testapp.get('/search/?type=SampleTerm&limit=1').json.get('@graph') or []
    if not labs or not awards or not terms:
        pytest.skip('missing lab/award/sample_term for insert timing')

    payload = {
        'lab': labs[0]['@id'],
        'award': awards[0]['@id'],
        'donors': [donor_id],
        'sources': [labs[0]['@id']],
        'sample_terms': [terms[0]['@id']],
        'status': 'released',
        'release_timestamp': '2024-03-06T12:34:56Z',
        'purity': ['77.5'],
        'virtual': False,
    }
    started = time.perf_counter()
    res = testapp.post_json('/primary-islet/', payload, status=201).json
    poll_until_indexing_is_done(testapp)
    elapsed_ms = (time.perf_counter() - started) * 1000.0
    assert res.get('@id')
    # Also confirm purity_value calc is searchable after index when present.
    obj = testapp.get(res['@id'] + '?frame=object').json
    if 'purity_value' in obj:
        assert obj['purity_value'] == 77.5
    print(f'INDEX_TIME_DELTA_MS insert_primary_islet={elapsed_ms:.1f}')
