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

@upgrade_step('human_donor', '13', '14')
def human_donor_13_14(value, system):
    # Bridge gap in upgrade path
    # No schema changes needed between v13 and v14
    pass

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
        
@upgrade_step('human_donor', '16', '17')
def human_donor_16_17(value, system):
    # https://igvf.atlassian.net/browse/IGVF-XXXX
    # Update multiple enum values for improved terminology and consistency
    
    # Update T1D stage enum values to include "level" terminology
    if 't1d_stage' in value:
        t1d_stage_mapping = {
            "At-risk: Single or transient autoantibody, normal glucose": 
                "At-risk: Single or transient autoantibody, normal glucose level",
            "Stage 1: Two or more autoantibodies, normal glucose metabolism": 
                "Stage 1: Two or more autoantibodies, normal glucose metabolism level",
            "Stage 2: Two or more autoantibodies, dysglycemia (e.g. HbA1c ≥ 5.7%)": 
                "Stage 2: Two or more autoantibodies, dysglycemia (e.g., HbA1c ≥ 5.7%)"
        }
        
        current_stage = value['t1d_stage']
        if current_stage in t1d_stage_mapping:
            value['t1d_stage'] = t1d_stage_mapping[current_stage]
    
    # Update diabetes_status_description enum values
    if 'diabetes_status_description' in value:
        diabetes_status_mapping = {
            "alström syndrome": "Alström syndrome",
            "cystic fibrosis diabetes": "cystic fibrosis-related diabetes",
            "non-diabetic": "control without diabetes"
        }
        
        current_status = value['diabetes_status_description']
        if current_status in diabetes_status_mapping:
            value['diabetes_status_description'] = diabetes_status_mapping[current_status]

    # Update ethnicities enum values
    if 'ethnicities' in value and isinstance(value['ethnicities'], list):
        ethnicities_mapping = {
            "Caucasian": "White"
        }
        updated_ethnicities = []
        for ethnicity in value['ethnicities']:
            if ethnicity in ethnicities_mapping:
                updated_ethnicities.append(ethnicities_mapping[ethnicity])
            else:
                updated_ethnicities.append(ethnicity)
        value['ethnicities'] = updated_ethnicities
    
    # Update donation_type enum values from abbreviations to full descriptions
    if 'donation_type' in value:
        donation_type_mapping = {
            "DCD": "Donation after Circulatory Death",
            "DBD": "Donation after Brain Death", 
            "NDD": "Natural Death Donation",
            "MAD": "Medical Assistance in Dying"
        }
        
        current_type = value['donation_type']
        if current_type in donation_type_mapping:
            value['donation_type'] = donation_type_mapping[current_type]


@upgrade_step('human_donor', '17', '18')
def human_donor_17_18(value, system):
    # Migrate glucose_loweing_theraphy to other_theraphy
    if 'glucose_loweing_theraphy' in value:
        glucose_therapy = value['glucose_loweing_theraphy']
        
        # Initialize other_theraphy if it doesn't exist
        if 'other_theraphy' not in value:
            value['other_theraphy'] = []
        
        # Ensure other_theraphy is a list
        if not isinstance(value['other_theraphy'], list):
            value['other_theraphy'] = []
        
        # Ensure glucose_loweing_theraphy is a list
        if not isinstance(glucose_therapy, list):
            glucose_therapy = [glucose_therapy] if glucose_therapy else []
        
        # Merge glucose therapy data into other_theraphy
        for therapy in glucose_therapy:
            if therapy and therapy not in value['other_theraphy']:
                value['other_theraphy'].append(therapy)
        
        # Remove the old field
        del value['glucose_loweing_theraphy']


@upgrade_step('human_donor', '18', '19')
@upgrade_step('rodent_donor', '12', '13')
def donor_sex_to_gender(value, system):
    # https://igvf.atlassian.net/browse/IGVF-XXXX
    # Rename 'sex' field to 'gender'
    if 'sex' in value:
        value['gender'] = value['sex']
        del value['sex']

@upgrade_step('human_donor', '19', '20')
def human_donor_19_20(value, system):
    # Migrate 'biological_sex' field to 'genetic_sex'
    if 'biological_sex' in value:
        value['genetic_sex'] = value['biological_sex']
        del value['biological_sex']

@upgrade_step('human_donor', '20', '21')
def human_donor_20_21(value, system):
    # Update family_history_of_diabetes enum values (capitalize and standardize)
    if 'family_history_of_diabetes' in value:
        mapping = {
            'true': 'TRUE',
            'false': 'FALSE',
            'na': '-',
            'n/a': '-',
            'unknown': '-',
            '': '-'
        }
        current_val = str(value['family_history_of_diabetes']).lower()
        if current_val in mapping:
            value['family_history_of_diabetes'] = mapping[current_val]
        elif current_val not in ['TRUE', 'FALSE', '-']:
            value['family_history_of_diabetes'] = '-'
    
    # Update donation_type enum values
    if 'donation_type' in value:
        mapping = {
            'Donation after Circulatory Death': 'Donation after circulatory death',
            'Donation after Brain Death': 'Donation after brain death',
            'Natural Death Donation': 'Natural death donation',
            'Medical Assistance in Dying': 'Medical assistance in dying',
            'DCD': 'Donation after circulatory death',
            'DBD': 'Donation after brain death',
            'NDD': 'Natural death donation',
            'MAD': 'Medical assistance in dying'
        }
        current_val = value['donation_type']
        if current_val in mapping:
            value['donation_type'] = mapping[current_val]
        elif current_val not in ['Donation after brain death', 'Donation after circulatory death',
                                 'Natural death donation', 'Medical assistance in dying', '-']:
            value['donation_type'] = '-'
    
    # Update gender enum values (capitalize)
    if 'gender' in value:
        mapping = {
            'male': 'Male',
            'female': 'Female',
            'other': 'Other'
        }
        current_val = str(value['gender']).lower()
        if current_val in mapping:
            value['gender'] = mapping[current_val]
        elif current_val not in ['Male', 'Female', 'Other', '-']:
            value['gender'] = '-'
    
    # Update genetic_sex enum values (capitalize and add Other/-)
    if 'genetic_sex' in value:
        mapping = {
            'male': 'Male',
            'female': 'Female',
            'other': 'Other'
        }
        current_val = str(value['genetic_sex']).lower()
        if current_val in mapping:
            value['genetic_sex'] = mapping[current_val]
        elif current_val not in ['Male', 'Female', 'Other', '-']:
            value['genetic_sex'] = '-'
    
    # Update diabetes_status_description enum values
    if 'diabetes_status_description' in value:
        mapping = {
            'type 1 diabetes': 'Type 1 Diabetes',
            'type 2 diabetes': 'Type 2 Diabetes',
            'control without diabetes': 'Control Without Diabetes',
            'diabetes unspecified': 'Diabetes Unspecified',
            'monogenic diabetes': 'Monogenic Diabetes',
            'gestational diabetes': 'Gestational Diabetes',
            'cystic fibrosis-related diabetes': 'Cystic Fibrosis-Related Diabetes',
            'cystic fibrosis diabetes': 'Cystic Fibrosis-Related Diabetes',
            'maturity onset diabetes of the young (mody)': 'Monogenic Diabetes',
            'non-diabetic': 'Control Without Diabetes'
        }
        current_val = str(value['diabetes_status_description']).lower()
        if current_val in mapping:
            value['diabetes_status_description'] = mapping[current_val]
        elif current_val not in ['Type 1 Diabetes', 'Type 2 Diabetes', 'Control Without Diabetes',
                                 'Diabetes Unspecified', 'Monogenic Diabetes', 'Gestational Diabetes',
                                 'Cystic Fibrosis-Related Diabetes', '-']:
            value['diabetes_status_description'] = '-'
    
    # Update t1d_stage enum values
    if 't1d_stage' in value:
        mapping = {
            'Stage 1: Two or more autoantibodies, normal glucose metabolism level': 
                'Stage 1: two or more autoantibodies, normal glucose metabolism level',
            'Stage 2: Two or more autoantibodies, dysglycemia (e.g., HbA1c ≥ 5.7%)': 
                'Stage 2: two or more autoantibodies, dysglycemia (e.g., HbA1c ≥ 5.7%)',
            'Stage 3: One or more autoantibodies and diagnostic hyperglycemia or T1D diagnosis': 
                'Stage 3: one or more autoantibodies and diagnostic hyperglycemia or T1D diagnosis',
            'No sufficient information to derive': 
                'No sufficient information to derive',
            'Conflicting diabetes evidence': 
                'Conflicting diabetes evidence',
            'At-risk: Single or transient autoantibody, normal glucose level': 
                'At-risk: single or transient autoantibody, normal glucose level',
            'At-risk: Single or transient autoantibody, normal glucose': 
                'At-risk: single or transient autoantibody, normal glucose level',
            'no sufficient information to derive': 
                'No sufficient information to derive',
            'no_stage': 
                'normal glucose level'
        }
        current_val = value['t1d_stage']
        if current_val in mapping:
            value['t1d_stage'] = mapping[current_val]
        elif current_val not in ['Stage 1: two or more autoantibodies, normal glucose metabolism level',
                                 'Stage 2: two or more autoantibodies, dysglycemia (e.g., HbA1c ≥ 5.7%)',
                                 'Stage 3: one or more autoantibodies and diagnostic hyperglycemia or T1D diagnosis',
                                 'No sufficient information to derive',
                                 'Conflicting diabetes evidence',
                                 'At-risk: single or transient autoantibody, normal glucose level',
                                 'normal glucose level']:
            value['t1d_stage'] = 'No sufficient information to derive'
