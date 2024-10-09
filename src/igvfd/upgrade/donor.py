from snovault import upgrade_step


@upgrade_step('human_donor', '1', '2')
@upgrade_step('rodent_donor', '1', '2')
def donor_1_2(value, system):
    # https://igvf.atlassian.net/browse/IGVF-221
    if 'parents' in value:
        if len(value['parents']) == 0:
            del value['parents']
    if 'external_resources' in value:
        if len(value['external_resources']) == 0:
            del value['external_resources']
    if 'aliases' in value:
        if len(value['aliases']) == 0:
            del value['aliases']
    if 'collections' in value:
        if len(value['collections']) == 0:
            del value['collections']
    if 'alternate_accessions' in value:
        if len(value['alternate_accessions']) == 0:
            del value['alternate_accessions']
    if 'documents' in value:
        if len(value['documents']) == 0:
            del value['documents']
    if 'references' in value:
        if len(value['references']) == 0:
            del value['references']


@upgrade_step('human_donor', '2', '3')
def human_donor_2_3(value, system):
    # https://igvf.atlassian.net/browse/IGVF-90
    if 'health_status_history' in value:
        del value['health_status_history']


@upgrade_step('human_donor', '3', '4')
def donor_3_4(value, system):
    # https://igvf.atlassian.net/browse/IGVF-321
    if 'ethnicity' in value:
        value['ethnicities'] = value['ethnicity']
        del value['ethnicity']


@upgrade_step('human_donor', '4', '5')
@upgrade_step('rodent_donor', '2', '3')
def donor_4_5(value, system):
    # https://igvf.atlassian.net/browse/IGVF-398
    if 'accession' in value:
        accession_prefix = value['accession'][0:6]
        accession_suffix = value['accession'][6:]
        value['accession'] = f'{accession_prefix}0{accession_suffix}A'


@upgrade_step('human_donor', '5', '6')
@upgrade_step('rodent_donor', '3', '4')
def donor_5_6(value, system):
    # https://igvf.atlassian.net/browse/IGVF-386
    if 'external_resources' in value:
        del value['external_resources']


@upgrade_step('rodent_donor', '4', '5')
def rodent_donor_4_5(value, system):
    # https://igvf.atlassian.net/browse/IGVF-384
    if 'individual_rodent' not in value:
        value['individual_rodent'] = False


@upgrade_step('human_donor', '6', '7')
@upgrade_step('rodent_donor', '5', '6')
def donor_6_7(value, system):
    # https://igvf.atlassian.net/browse/IGVF-444
    if 'traits' in value:
        traits = value['traits']
        new_notes_value = ''
        if 'notes' in value:
            new_notes_value = value.get('notes')
        for current_trait in traits:
            if len(new_notes_value) > 0:
                new_notes_value += '  '
            new_notes_value += f'traits: {current_trait}'
        value['notes'] = new_notes_value
        del value['traits']


@upgrade_step('rodent_donor', '6', '7')
def rodent_donor_6_7(value, system):
    # https://igvf.atlassian.net/browse/IGVF-408
    if 'parents' in value:
        parents = value['parents']
        if 'notes' in value:
            new_notes_value = value.get('notes')
        for parent in parents:
            if len(new_notes_value) > 0:
                new_notes_value += '  '
            new_notes_value += f'parents: {parent}'
        value['notes'] = new_notes_value
        del value['parents']


@upgrade_step('human_donor', '7', '8')
def human_donor_7_8(value, system):
    # https://igvf.atlassian.net/browse/IGVF-408
    if 'parents' in value:
        parents = value['parents']
        related_donors = []
        for parent in parents:
            related_donors.append(
                {
                    'donor': parent,
                    'relationship_type': 'parent'
                }
            )
        value['related_donors'] = related_donors
        del value['parents']


@upgrade_step('human_donor', '8', '9')
@upgrade_step('rodent_donor', '7', '8')
def donor_8_9(value, system):
    # https://igvf.atlassian.net/browse/IGVF-726
    # This upgrade is to update previous data with
    # default value for 'virtual' property.
    # The default value will be automatically populated.
    return


@upgrade_step('human_donor', '9', '10')
def human_donor_9_10(value, system):
    # https://igvf.atlassian.net/browse/IGVF-765
    if 'human_donor_identifier' in value:
        value['human_donor_identifiers'] = value['human_donor_identifier']
        del value['human_donor_identifier']


@upgrade_step('human_donor', '10', '11')
@upgrade_step('rodent_donor', '8', '9')
def donor_10_11(value, system):
    # https://igvf.atlassian.net/browse/IGVF-802
    if 'references' in value:
        value['publication_identifiers'] = value['references']
        del value['references']


@upgrade_step('rodent_donor', '9', '10')
def rodent_donor_9_10(value, system):
    # https://igvf.atlassian.net/browse/IGVF-895
    # Source property is pluralized
    if 'source' in value:
        value['sources'] = [value['source']]
        del value['source']


@upgrade_step('human_donor', '11', '12')
@upgrade_step('rodent_donor', '10', '11')
def donor_11_12(value, system):
    # https://igvf.atlassian.net/browse/IGVF-1170
    if 'description' in value:
        if value['description'] == '':
            del value['description']


@upgrade_step('human_donor', '12', '13')
@upgrade_step('rodent_donor', '11', '12')
def donor_12_13(value, system):
    # https://igvf.atlassian.net/browse/IGVF-1494
    if value['status'] in ['released', 'archived', 'revoked'] and 'release_timestamp' not in value:
        value['release_timestamp'] = '2024-03-06T12:34:56Z'
        notes = value.get('notes', '')
        notes += f'This object\'s release_timestamp has been set to 2024-03-06T12:34:56Z'
        value['notes'] = notes.strip()

@upgrade_step('human_donor', '14', '15')
def human_donor_14_15(value, system):
    # Convert family_history_of_diabetes boolean to string
    if 'family_history_of_diabetes' in value:
        # Check if it's a boolean and convert it to a string
        if isinstance(value['family_history_of_diabetes'], bool):
            value['family_history_of_diabetes'] = 'true' if value['family_history_of_diabetes'] else 'false'
        elif value['family_history_of_diabetes'] is None:
            value['family_history_of_diabetes'] = 'N/A'
    # Convert diabetes_duration from number to string
    if 'diabetes_duration' in value:
        # Check if it's a number and convert it to a string
        if isinstance(value['diabetes_duration'], (int, float)):
            value['diabetes_duration'] = str(value['diabetes_duration'])
        # Handle null or missing values if necessary
        elif value['diabetes_duration'] is None:
            value['diabetes_duration'] = 'N/A'
    # Ensure Other Tissues Available defaults to an empty array if not present
    if 'other_tissues_available' not in value or not isinstance(value['other_tissues_available'], list):
        value['other_tissues_available'] = []
    # Ensure Diabetes Status defaults to an empty array if not present
    if 'diabetes_status' not in value or not isinstance(value['diabetes_status'], list):
        value['diabetes_status'] = []
@upgrade_step('human_donor', '15', '16')
def human_donor_15_16(value, system):
    # Update genetic_ethnicities to include percentage
    if 'genetic_ethnicities' in value:
        updated_ethnicities = []
        for ethnicity in value['genetic_ethnicities']:
            # If ethnicity is a string, convert it to an object with 100% as the default percentage
            if isinstance(ethnicity, str):
                updated_ethnicities.append({
                    "ethnicity": ethnicity,
                    "percentage": 100
                })
            else:
                # In case of unexpected data types, retain as is (or handle as needed)
                updated_ethnicities.append(ethnicity)
        value['genetic_ethnicities'] = updated_ethnicities

        
