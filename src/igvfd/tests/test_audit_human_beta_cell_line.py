import pytest
from snovault.auditor import AuditFailure
from igvfd.audit.human_beta_cell_line import (
    audit_required_fields_check,
    audit_dependent_fields_check,
    audit_status_release_timestamp_check,
    audit_classifications_format_check,
    audit_sample_name_format_check,
)


class MockSystem:
    def __init__(self, path):
        self.path = path
        self.request = None


def test_audit_required_fields_check_missing_fields():
    """Test that missing required fields trigger audit failures."""
    value = {
        '@id': '/human-beta-cell-line/test/',
        'award': '/awards/test/',
        # Missing 'lab' and 'sample_name'
    }
    system = MockSystem('/human-beta-cell-line/test/')
    
    failures = list(audit_required_fields_check(value, system))
    assert len(failures) == 1
    assert isinstance(failures[0], AuditFailure)
    assert failures[0].category == 'missing required field'
    assert 'lab' in failures[0].detail
    assert 'sample_name' in failures[0].detail


def test_audit_required_fields_check_all_present():
    """Test that all required fields present passes audit."""
    value = {
        '@id': '/human-beta-cell-line/test/',
        'award': '/awards/test/',
        'lab': '/labs/test/',
        'sample_name': 'EndoC-Bh1'
    }
    system = MockSystem('/human-beta-cell-line/test/')
    
    failures = list(audit_required_fields_check(value, system))
    assert len(failures) == 0


def test_audit_dependent_fields_check_lot_id_missing_product_id():
    """Test that lot_id without product_id triggers audit failure."""
    value = {
        '@id': '/human-beta-cell-line/test/',
        'lot_id': '12345',
        # Missing 'product_id'
    }
    system = MockSystem('/human-beta-cell-line/test/')
    
    failures = list(audit_dependent_fields_check(value, system))
    assert len(failures) == 1
    assert isinstance(failures[0], AuditFailure)
    assert failures[0].category == 'missing dependent field'
    assert 'lot_id' in failures[0].detail
    assert 'product_id' in failures[0].detail


def test_audit_dependent_fields_check_passage_number_missing_growth_medium():
    """Test that passage_number without growth_medium triggers audit failure."""
    value = {
        '@id': '/human-beta-cell-line/test/',
        'passage_number': 15,
        # Missing 'growth_medium'
    }
    system = MockSystem('/human-beta-cell-line/test/')
    
    failures = list(audit_dependent_fields_check(value, system))
    assert len(failures) == 1
    assert isinstance(failures[0], AuditFailure)
    assert failures[0].category == 'missing dependent field'
    assert 'passage_number' in failures[0].detail
    assert 'growth_medium' in failures[0].detail


def test_audit_status_release_timestamp_check_missing_timestamp():
    """Test that released status without release_timestamp triggers audit failure."""
    value = {
        '@id': '/human-beta-cell-line/test/',
        'status': 'released',
        # Missing 'release_timestamp'
    }
    system = MockSystem('/human-beta-cell-line/test/')
    
    failures = list(audit_status_release_timestamp_check(value, system))
    assert len(failures) == 1
    assert isinstance(failures[0], AuditFailure)
    assert failures[0].category == 'missing release timestamp'


def test_audit_classifications_format_check_not_array():
    """Test that classifications as string triggers audit failure."""
    value = {
        '@id': '/human-beta-cell-line/test/',
        'classifications': 'cell line',  # Should be array
    }
    system = MockSystem('/human-beta-cell-line/test/')
    
    failures = list(audit_classifications_format_check(value, system))
    assert len(failures) == 1
    assert isinstance(failures[0], AuditFailure)
    assert failures[0].category == 'incorrect classifications format'


def test_audit_classifications_format_check_correct_format():
    """Test that correct classifications format passes audit."""
    value = {
        '@id': '/human-beta-cell-line/test/',
        'classifications': ['cell line'],
    }
    system = MockSystem('/human-beta-cell-line/test/')
    
    failures = list(audit_classifications_format_check(value, system))
    assert len(failures) == 0


def test_audit_sample_name_format_check_empty_name():
    """Test that empty sample name triggers audit failure."""
    value = {
        '@id': '/human-beta-cell-line/test/',
        'sample_name': '   ',  # Whitespace only
    }
    system = MockSystem('/human-beta-cell-line/test/')
    
    failures = list(audit_sample_name_format_check(value, system))
    assert len(failures) == 1
    assert isinstance(failures[0], AuditFailure)
    assert failures[0].category == 'invalid sample name format'


def test_audit_sample_name_format_check_valid_name():
    """Test that valid sample name passes audit."""
    value = {
        '@id': '/human-beta-cell-line/test/',
        'sample_name': 'EndoC-Bh1',
    }
    system = MockSystem('/human-beta-cell-line/test/')
    
    failures = list(audit_sample_name_format_check(value, system))
    assert len(failures) == 0
