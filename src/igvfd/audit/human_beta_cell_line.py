from snovault.auditor import (
    audit_checker,
    AuditFailure,
)
from .formatter import (
    audit_link,
    path_to_text,
    get_audit_description,
)


@audit_checker('HumanBetaCellLines', frame='object')
def audit_required_fields_check(value, system):
    '''
    [
        {
            "audit_description": "Human beta cell lines are expected to have all required fields present.",
            "audit_category": "missing required field",
            "audit_level": "ERROR"
        }
    ]
    '''
    description = get_audit_description(audit_required_fields_check)
    value_id = system.get('path')
    
    # Check for always required fields
    required_fields = ['award', 'lab', 'sample_name']
    missing_fields = []
    
    for field in required_fields:
        if field not in value or not value[field]:
            missing_fields.append(field)
    
    if missing_fields:
        detail = (
            f'Human beta cell line {audit_link(path_to_text(value_id), value_id)} '
            f'is missing required field(s): {", ".join(missing_fields)}.'
        )
        yield AuditFailure('missing required field', f'{detail} {description}', level='ERROR')


@audit_checker('HumanBetaCellLines', frame='object')
def audit_dependent_fields_check(value, system):
    '''
    [
        {
            "audit_description": "Human beta cell lines are expected to have dependent fields when their dependencies are present.",
            "audit_category": "missing dependent field",
            "audit_level": "ERROR"
        }
    ]
    '''
    description = get_audit_description(audit_dependent_fields_check)
    value_id = system.get('path')
    
    # Check lot_id requires product_id
    if 'lot_id' in value and value['lot_id'] and ('product_id' not in value or not value['product_id']):
        detail = (
            f'Human beta cell line {audit_link(path_to_text(value_id), value_id)} '
            f'has `lot_id` specified but is missing required `product_id`.'
        )
        yield AuditFailure('missing dependent field', f'{detail} {description}', level='ERROR')
    
    # Check product_id requires lot_id
    if 'product_id' in value and value['product_id'] and ('lot_id' not in value or not value['lot_id']):
        detail = (
            f'Human beta cell line {audit_link(path_to_text(value_id), value_id)} '
            f'has `product_id` specified but is missing required `lot_id`.'
        )
        yield AuditFailure('missing dependent field', f'{detail} {description}', level='ERROR')
    
    # Check sorted_from requires sorted_from_detail
    if 'sorted_from' in value and value['sorted_from'] and ('sorted_from_detail' not in value or not value['sorted_from_detail']):
        detail = (
            f'Human beta cell line {audit_link(path_to_text(value_id), value_id)} '
            f'has `sorted_from` specified but is missing required `sorted_from_detail`.'
        )
        yield AuditFailure('missing dependent field', f'{detail} {description}', level='ERROR')
    
    # Check sorted_from_detail requires sorted_from
    if 'sorted_from_detail' in value and value['sorted_from_detail'] and ('sorted_from' not in value or not value['sorted_from']):
        detail = (
            f'Human beta cell line {audit_link(path_to_text(value_id), value_id)} '
            f'has `sorted_from_detail` specified but is missing required `sorted_from`.'
        )
        yield AuditFailure('missing dependent field', f'{detail} {description}', level='ERROR')
    
    # Check starting_amount requires starting_amount_units
    if 'starting_amount' in value and value['starting_amount'] is not None and ('starting_amount_units' not in value or not value['starting_amount_units']):
        detail = (
            f'Human beta cell line {audit_link(path_to_text(value_id), value_id)} '
            f'has `starting_amount` specified but is missing required `starting_amount_units`.'
        )
        yield AuditFailure('missing dependent field', f'{detail} {description}', level='ERROR')
    
    # Check starting_amount_units requires starting_amount
    if 'starting_amount_units' in value and value['starting_amount_units'] and ('starting_amount' not in value or value['starting_amount'] is None):
        detail = (
            f'Human beta cell line {audit_link(path_to_text(value_id), value_id)} '
            f'has `starting_amount_units` specified but is missing required `starting_amount`.'
        )
        yield AuditFailure('missing dependent field', f'{detail} {description}', level='ERROR')
    
    # Check moi requires construct_library_sets
    if 'moi' in value and value['moi'] is not None and ('construct_library_sets' not in value or not value['construct_library_sets']):
        detail = (
            f'Human beta cell line {audit_link(path_to_text(value_id), value_id)} '
            f'has `moi` specified but is missing required `construct_library_sets`.'
        )
        yield AuditFailure('missing dependent field', f'{detail} {description}', level='ERROR')
    
    # Check time_post_library_delivery requires time_post_library_delivery_units and construct_library_sets
    if 'time_post_library_delivery' in value and value['time_post_library_delivery'] is not None:
        missing_deps = []
        if 'time_post_library_delivery_units' not in value or not value['time_post_library_delivery_units']:
            missing_deps.append('time_post_library_delivery_units')
        if 'construct_library_sets' not in value or not value['construct_library_sets']:
            missing_deps.append('construct_library_sets')
        
        if missing_deps:
            detail = (
                f'Human beta cell line {audit_link(path_to_text(value_id), value_id)} '
                f'has `time_post_library_delivery` specified but is missing required field(s): {", ".join(missing_deps)}.'
            )
            yield AuditFailure('missing dependent field', f'{detail} {description}', level='ERROR')
    
    # Check time_post_library_delivery_units requires time_post_library_delivery and construct_library_sets
    if 'time_post_library_delivery_units' in value and value['time_post_library_delivery_units']:
        missing_deps = []
        if 'time_post_library_delivery' not in value or value['time_post_library_delivery'] is None:
            missing_deps.append('time_post_library_delivery')
        if 'construct_library_sets' not in value or not value['construct_library_sets']:
            missing_deps.append('construct_library_sets')
        
        if missing_deps:
            detail = (
                f'Human beta cell line {audit_link(path_to_text(value_id), value_id)} '
                f'has `time_post_library_delivery_units` specified but is missing required field(s): {", ".join(missing_deps)}.'
            )
            yield AuditFailure('missing dependent field', f'{detail} {description}', level='ERROR')
    
    # Check age fields dependencies
    age_fields = ['lower_bound_age', 'upper_bound_age', 'age_units']
    present_age_fields = [field for field in age_fields if field in value and value[field] is not None]
    
    if len(present_age_fields) > 0 and len(present_age_fields) < 3:
        missing_age_fields = [field for field in age_fields if field not in present_age_fields]
        detail = (
            f'Human beta cell line {audit_link(path_to_text(value_id), value_id)} '
            f'has age field(s) {", ".join(present_age_fields)} specified but is missing required field(s): {", ".join(missing_age_fields)}.'
        )
        yield AuditFailure('missing dependent field', f'{detail} {description}', level='ERROR')
    
    # Check passage_number requires growth_medium
    if 'passage_number' in value and value['passage_number'] is not None and ('growth_medium' not in value or not value['growth_medium']):
        detail = (
            f'Human beta cell line {audit_link(path_to_text(value_id), value_id)} '
            f'has `passage_number` specified but is missing required `growth_medium`.'
        )
        yield AuditFailure('missing dependent field', f'{detail} {description}', level='ERROR')


@audit_checker('HumanBetaCellLines', frame='object')
def audit_status_release_timestamp_check(value, system):
    '''
    [
        {
            "audit_description": "Human beta cell lines with released, archived, or revoked status should have release_timestamp specified.",
            "audit_category": "missing release timestamp",
            "audit_level": "ERROR"
        }
    ]
    '''
    description = get_audit_description(audit_status_release_timestamp_check)
    value_id = system.get('path')
    
    if 'status' in value and value['status'] in ['released', 'archived', 'revoked']:
        if 'release_timestamp' not in value or not value['release_timestamp']:
            detail = (
                f'Human beta cell line {audit_link(path_to_text(value_id), value_id)} '
                f'has status `{value["status"]}` but is missing required `release_timestamp`.'
            )
            yield AuditFailure('missing release timestamp', f'{detail} {description}', level='ERROR')


@audit_checker('HumanBetaCellLines', frame='object')
def audit_classifications_format_check(value, system):
    '''
    [
        {
            "audit_description": "Human beta cell lines are expected to have classifications as an array.",
            "audit_category": "incorrect classifications format",
            "audit_level": "ERROR"
        }
    ]
    '''
    description = get_audit_description(audit_classifications_format_check)
    value_id = system.get('path')
    
    if 'classifications' in value and value['classifications']:
        if not isinstance(value['classifications'], list):
            detail = (
                f'Human beta cell line {audit_link(path_to_text(value_id), value_id)} '
                f'has `classifications` as {type(value["classifications"]).__name__} but it should be an array.'
            )
            yield AuditFailure('incorrect classifications format', f'{detail} {description}', level='ERROR')
        elif len(value['classifications']) != 1 or value['classifications'][0] != 'cell line':
            detail = (
                f'Human beta cell line {audit_link(path_to_text(value_id), value_id)} '
                f'has `classifications` {value["classifications"]} but should be ["cell line"].'
            )
            yield AuditFailure('incorrect classifications format', f'{detail} {description}', level='WARNING')


@audit_checker('HumanBetaCellLines', frame='object')
def audit_sample_name_format_check(value, system):
    '''
    [
        {
            "audit_description": "Human beta cell lines are expected to have a valid sample name format.",
            "audit_category": "invalid sample name format",
            "audit_level": "WARNING"
        }
    ]
    '''
    description = get_audit_description(audit_sample_name_format_check)
    value_id = system.get('path')
    
    if 'sample_name' in value and value['sample_name']:
        sample_name = value['sample_name']
        # Check if sample name follows common cell line naming patterns
        if not sample_name or len(sample_name.strip()) == 0:
            detail = (
                f'Human beta cell line {audit_link(path_to_text(value_id), value_id)} '
                f'has empty or whitespace-only `sample_name`.'
            )
            yield AuditFailure('invalid sample name format', f'{detail} {description}', level='WARNING')
        elif not any(char.isalnum() for char in sample_name):
            detail = (
                f'Human beta cell line {audit_link(path_to_text(value_id), value_id)} '
                f'has `sample_name` "{sample_name}" that contains no alphanumeric characters.'
            )
            yield AuditFailure('invalid sample name format', f'{detail} {description}', level='WARNING')
