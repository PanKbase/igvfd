import pytest

from igvfd.types.file import get_download_file_extension


def test_file_download_has_uploading_file_credentials(testapp, sequence_file):
    assert 'upload_credentials' in sequence_file
    accession = sequence_file['accession']
    assert sequence_file['href'] == f'/sequence-files/{accession}/@@download/{accession}.fastq.gz'
    response = testapp.patch_json(
        sequence_file['@id'],
        {
            'upload_status': 'validated'
        }
    )
    updated_sequence_file = response.json['@graph'][0]
    assert 'upload_credentials' not in updated_sequence_file


def test_file_download_view_redirect(testapp, sequence_file):
    response = testapp.get(
        sequence_file['href'],
        extra_environ={
            'HTTP_X_FORWARDED_FOR': '100.100.100.100'
        }
    )
    assert '307 Temporary Redirect' in str(response.body)
    assert 'X-Accel-Redirect' not in response.headers
    assert 'http://localstack:4566/igvf-files-local' in response.headers['Location']


def test_file_download_view_proxy_range(testapp, sequence_file):
    response = testapp.get(
        sequence_file['href'],
        headers={
            'Range': 'bytes=0-4444'
        },
        extra_environ={
            'HTTP_X_FORWARDED_FOR': '100.100.100.100'
        },
    )
    assert '307 Temporary Redirect' in str(response.body)
    assert 'X-Accel-Redirect' not in response.headers


def test_file_download_view_soft_redirect(testapp, sequence_file):
    response = testapp.get(
        sequence_file['href'] + '?soft=True'
    )
    assert response.json['@type'][0] == 'SoftRedirect'
    assert 'location' in response.json


def test_file_download_regenerating_credentials_uploading_file_not_found(testapp, sequence_file, root):
    item = root.get_by_uuid(
        sequence_file['uuid']
    )
    properties = item.upgrade_properties()
    # Clear the external sheet.
    item.update(
        properties,
        sheets={
            'external': {},
        }
    )
    testapp.post_json(
        sequence_file['@id'] + '@@upload',
        {},
        status=404
    )


def test_file_download_file_not_found(testapp, sequence_file, root):
    item = root.get_by_uuid(
        sequence_file['uuid']
    )
    properties = item.upgrade_properties()
    # Clear the external sheet.
    item.update(
        properties,
        sheets={
            'external': {}
        }
    )
    testapp.get(
        sequence_file['href'],
        status=404
    )


def _clear_external_sheet(root, file_item):
    item = root.get_by_uuid(file_item['uuid'])
    properties = item.upgrade_properties()
    item.update(properties, sheets={'external': {}})


@pytest.mark.parametrize('file_url,file_format,expected_ext', [
    ('https://example.com/data/peaks.tsv', 'tsv', '.tsv'),
    ('https://example.com/data/peaks.tsv.gz', 'tsv', '.tsv.gz'),
    ('https://example.com/data/regions.bed', 'bed', '.bed'),
    ('https://example.com/data/matrix.mtx', 'mtx', '.mtx'),
    ('https://example.com/data/signal.bigWig', 'bigWig', '.bigWig'),
    ('https://example.com/data/signal.bw', 'bigWig', '.bw'),
])
def test_get_download_file_extension_from_file_url(file_url, file_format, expected_ext):
    assert get_download_file_extension(file_format, file_url) == expected_ext


def test_get_download_file_extension_falls_back_to_format_map():
    assert get_download_file_extension('tsv') == '.tsv.gz'
    assert get_download_file_extension('bigWig', None) == '.bigWig'


def test_file_download_falls_back_to_file_url(testapp, tabular_file, root):
    file_url = 'https://pankbase-data-v1.s3.amazonaws.com/analysis/peaks.tsv'
    testapp.patch_json(
        tabular_file['@id'],
        {
            'file_url': file_url,
            'upload_status': 'validated',
            'file_size': 123,
        },
        status=200,
    )
    _clear_external_sheet(root, tabular_file)
    res = testapp.get(tabular_file['@id'])
    accession = res.json['accession']
    assert res.json['href'] == f'/tabular-files/{accession}/@@download/{accession}.tsv'
    response = testapp.get(res.json['href'])
    assert response.status_code == 307
    assert response.headers['Location'] == file_url


def test_file_download_file_url_soft_redirect(testapp, tabular_file, root):
    file_url = 'https://pankbase-data-v1.s3.amazonaws.com/analysis/peaks.tsv.gz'
    testapp.patch_json(
        tabular_file['@id'],
        {
            'file_url': file_url,
            'upload_status': 'validated',
            'file_size': 123,
        },
        status=200,
    )
    _clear_external_sheet(root, tabular_file)
    res = testapp.get(tabular_file['@id'])
    response = testapp.get(res.json['href'] + '?soft=True')
    assert response.json['@type'][0] == 'SoftRedirect'
    assert response.json['location'] == file_url
    assert response.json['expires'] is None


def test_file_download_external_sheet_unchanged(testapp, tabular_file, root):
    file_url = 'https://pankbase-data-v1.s3.amazonaws.com/analysis/peaks.tsv'
    testapp.patch_json(
        tabular_file['@id'],
        {
            'file_url': file_url,
            'upload_status': 'validated',
            'file_size': 123,
        },
        status=200,
    )
    item = root.get_by_uuid(tabular_file['uuid'])
    properties = item.upgrade_properties()
    # Usable non-pankbase-files sheet: keep existing presigned-URL behavior.
    item.update(
        properties,
        sheets={
            'external': {
                'service': 's3',
                'bucket': 'pankbase-files-local',
                'key': '2024/01/01/uuid/file.tsv.gz',
            }
        },
    )
    res = testapp.get(tabular_file['@id'])
    response = testapp.get(
        res.json['href'],
        extra_environ={
            'HTTP_X_FORWARDED_FOR': '100.100.100.100'
        },
    )
    assert response.status_code == 307
    assert 'pankbase-files-local' in response.headers['Location']
    assert response.headers['Location'] != file_url


def test_file_download_prefers_file_url_for_pankbase_files_bucket(testapp, tabular_file, root):
    file_url = 'https://pankbase-data-v1.s3.amazonaws.com/analysis/peaks.tsv'
    testapp.patch_json(
        tabular_file['@id'],
        {
            'file_url': file_url,
            'upload_status': 'validated',
            'file_size': 123,
        },
        status=200,
    )
    item = root.get_by_uuid(tabular_file['uuid'])
    properties = item.upgrade_properties()
    # Simulate broken upload-bucket sheet whose key 404s in prod.
    item.update(
        properties,
        sheets={
            'external': {
                'service': 's3',
                'bucket': 'pankbase-files',
                'key': '2024/01/01/dead/key.tsv.gz',
            }
        },
    )
    res = testapp.get(tabular_file['@id'])
    response = testapp.get(res.json['href'])
    assert response.status_code == 307
    assert response.headers['Location'] == file_url


@pytest.mark.parametrize('file_url,expected_ext', [
    ('https://example.com/x.tsv', '.tsv'),
    ('https://example.com/x.tsv.gz', '.tsv.gz'),
])
def test_file_href_extension_from_file_url_tabular(testapp, tabular_file, file_url, expected_ext):
    testapp.patch_json(
        tabular_file['@id'],
        {
            'file_url': file_url,
            'upload_status': 'validated',
            'file_size': 123,
        },
        status=200,
    )
    res = testapp.get(tabular_file['@id'])
    accession = res.json['accession']
    assert res.json['href'].endswith(f'/@@download/{accession}{expected_ext}')


def test_file_href_extension_from_file_url_bed(testapp, tabular_file):
    testapp.patch_json(
        tabular_file['@id'],
        {
            'file_format': 'bed',
            'file_format_type': 'bed3',
            'assembly': 'GRCh38',
            'file_url': 'https://example.com/x.bed',
            'upload_status': 'validated',
            'file_size': 123,
        },
        status=200,
    )
    res = testapp.get(tabular_file['@id'])
    accession = res.json['accession']
    assert res.json['href'].endswith(f'/@@download/{accession}.bed')


def test_file_href_extension_from_file_url_mtx(testapp, lab, award, analysis_set_with_sample, reference_file):
    item = {
        'award': award['@id'],
        'lab': lab['@id'],
        'md5sum': '01b08bb5485ac730df19af55ba4bb0aa',
        'file_format': 'mtx',
        'file_set': analysis_set_with_sample['@id'],
        'file_size': 100,
        'content_type': 'sparse gene count matrix',
        'reference_files': [reference_file['@id']],
        'dimension1': 'cell',
        'dimension2': 'gene',
        'file_url': 'https://example.com/counts.mtx',
        'upload_status': 'validated',
    }
    res = testapp.post_json('/matrix_file', item, status=201).json['@graph'][0]
    accession = res['accession']
    assert res['href'] == f'/matrix-files/{accession}/@@download/{accession}.mtx'


@pytest.mark.parametrize('file_url,expected_ext', [
    ('https://example.com/signal.bigWig', '.bigWig'),
    ('https://example.com/signal.bw', '.bw'),
])
def test_file_href_extension_from_file_url_bigwig(testapp, signal_file, file_url, expected_ext):
    testapp.patch_json(
        signal_file['@id'],
        {
            'file_url': file_url,
            'upload_status': 'validated',
        },
        status=200,
    )
    res = testapp.get(signal_file['@id'])
    accession = res.json['accession']
    assert res.json['href'].endswith(f'/@@download/{accession}{expected_ext}')
