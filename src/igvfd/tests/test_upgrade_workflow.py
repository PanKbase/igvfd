import pytest


def test_workflow_upgrade_1_2(upgrader, workflow_v1):
    ids = workflow_v1['references']
    value = upgrader.upgrade(
        'workflow', workflow_v1,
        current_version='1', target_version='2')
    assert value['schema_version'] == '2'
    assert 'publication_identifiers' in value and value['publication_identifiers'] == ids
    assert 'references' not in value


def test_workflow_upgrade_2_3(upgrader, workflow_v2):
    value = upgrader.upgrade(
        'workflow', workflow_v2,
        current_version='2', target_version='3')
    assert value['schema_version'] == '3'
    assert 'description' not in value


def test_workflow_upgrade_3_4(upgrader, workflow_v3):
    value = upgrader.upgrade(
        'workflow', workflow_v3,
        current_version='3', target_version='4')
    assert value['schema_version'] == '4'
    assert value['release_timestamp'] == '2024-03-06T12:34:56Z'
    assert value['notes'] == 'This object\'s release_timestamp has been set to 2024-03-06T12:34:56Z'


def test_workflow_upgrade_4_5(upgrader, workflow_v4):
    value = upgrader.upgrade(
        'workflow', workflow_v4,
        current_version='4', target_version='5')
    assert value['schema_version'] == '5'
    assert isinstance(value['award'], list)
    assert len(value['award']) == 1
    assert value['award'][0] == '/awards/HG012012'
