import pytest


def test_audit_upload_status(testapp, reference_file):
    testapp.patch_json(
        reference_file['@id'],
        {
            'upload_status': 'pending'
        },
        status=200,
    )
    res = testapp.get(reference_file['@id'] + '@@audit')
    assert any(
        audit['category'] == 'upload status not validated'
        for audit in res.json['audit'].get('ERROR', {})
    )
    testapp.patch_json(
        reference_file['@id'],
        {
            'upload_status': 'invalidated',
            'external': True
        },
        status=200,
    )
    res = testapp.get(reference_file['@id'] + '@@audit')
    assert any(
        audit['category'] == 'upload status not validated'
        for audit in res.json['audit'].get('WARNING', {})
    )
    assert all(
        audit['category'] != 'upload status not validated'
        for audit in res.json['audit'].get('ERROR', {})
    )
    testapp.patch_json(
        reference_file['@id'],
        {
            'upload_status': 'validated',
            'file_size': 123,

        },
        status=200,
    )
    res = testapp.get(reference_file['@id'] + '@@audit')
    assert all(
        audit['category'] != 'upload status not validated'
        for audit in res.json['audit'].get('WARNING', {})
    )
    assert all(
        audit['category'] != 'upload status not validated'
        for audit in res.json['audit'].get('ERROR', {})
    )


def test_audit_file_format_specifications(testapp, matrix_file, experimental_protocol_document):
    testapp.patch_json(
        matrix_file['@id'],
        {
            'file_format_specifications': [experimental_protocol_document['@id']]
        }
    )
    res = testapp.get(matrix_file['@id'] + '@@audit')
    assert any(
        audit['category'] == 'inconsistent document type'
        for audit in res.json['audit'].get('ERROR', {})
    )
    testapp.patch_json(
        experimental_protocol_document['@id'],
        {
            'document_type': 'file format specification'
        }
    )
    res = testapp.get(matrix_file['@id'] + '@@audit')
    assert all(
        audit['category'] != 'inconsistent document type'
        for audit in res.json['audit'].get('ERROR', {})
    )


def test_audit_external_identifiers(testapp, model_file):
    testapp.patch_json(
        model_file['@id'],
        {
            'externally_hosted': True,
            'external_host_url': 'http://test_url'
        }
    )
    res = testapp.get(model_file['@id'] + '@@audit')
    assert any(
        audit['category'] == 'missing dbxrefs'
        for audit in res.json['audit'].get('WARNING', {})
    )
    testapp.patch_json(
        model_file['@id'],
        {
            'dbxrefs': ['Kipoi:test']
        }
    )
    res = testapp.get(model_file['@id'] + '@@audit')
    assert all(
        audit['category'] != 'missing dbxrefs'
        for audit in res.json['audit'].get('WARNING', {})
    )


def test_audit_external_reference_files(testapp, reference_file):
    testapp.patch_json(
        reference_file['@id'],
        {
            'external': True
        }
    )
    res = testapp.get(reference_file['@id'] + '@@audit')
    assert any(
        audit['category'] == 'missing dbxrefs'
        for audit in res.json['audit'].get('WARNING', {})
    )
    testapp.patch_json(
        reference_file['@id'],
        {
            'dbxrefs': ['ENCODE:ENCFF743WOO']
        }
    )
    res = testapp.get(reference_file['@id'] + '@@audit')
    assert all(
        audit['category'] != 'missing dbxrefs'
        for audit in res.json['audit'].get('WARNING', {})
    )


def test_audit_validated_file_missing_download_location(testapp, tabular_file, root):
    testapp.patch_json(
        tabular_file['@id'],
        {
            'upload_status': 'validated',
            'file_size': 123,
        },
        status=200,
    )
    item = root.get_by_uuid(tabular_file['uuid'])
    properties = item.upgrade_properties()
    item.update(properties, sheets={'external': {}})
    res = testapp.get(tabular_file['@id'] + '@@audit')
    assert any(
        audit['category'] == 'missing download location'
        for audit in res.json['audit'].get('ERROR', {})
    )


def test_audit_validated_file_with_file_url_has_download_location(testapp, tabular_file, root):
    testapp.patch_json(
        tabular_file['@id'],
        {
            'upload_status': 'validated',
            'file_size': 123,
            'file_url': 'https://pankbase-data-v1.s3.amazonaws.com/analysis/peaks.tsv',
        },
        status=200,
    )
    item = root.get_by_uuid(tabular_file['uuid'])
    properties = item.upgrade_properties()
    item.update(properties, sheets={'external': {}})
    res = testapp.get(tabular_file['@id'] + '@@audit')
    assert all(
        audit['category'] != 'missing download location'
        for audit in res.json['audit'].get('ERROR', {})
    )
