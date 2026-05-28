def test_primary_islet_upgrade_20_21(upgrader):
    value = {
        'schema_version': '20',
        'shipping_temperature': 4,
    }
    value = upgrader.upgrade(
        'primary_islet',
        value,
        current_version='20',
        target_version='21',
    )
    assert value['schema_version'] == '21'
    assert value['shipping_temperature'] == '4'


def test_primary_islet_upgrade_20_21_preserves_string(upgrader):
    value = {
        'schema_version': '20',
        'shipping_temperature': '6-10',
    }
    value = upgrader.upgrade(
        'primary_islet',
        value,
        current_version='20',
        target_version='21',
    )
    assert value['schema_version'] == '21'
    assert value['shipping_temperature'] == '6-10'
