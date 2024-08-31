## Changelog for *`human_donor.json`*
### Minor changes since schema version 14
* change desired field to tier 2 and add tier 3 which are optional tiers are tier 1, tier 2, tier 3. Audits accordingly
* add family_history_of_diabetes (boolean), family_history_of_diabetes_relationship (array string) 
* add enum to donnation type and glucose lowering therapy
### Minor changes since schema version 14
* add desired field tiers are required, desired and optional. Audits accordingly
* update description to clarify that certain fields are marked as 'required', others as 'desired', and all remaining fields are considered optional. 
### Minor changes since schema version 14
* add RRID: pattern `^RRID:[A-Z]{4}\d{8}$`
 
### Schema version 14

*Update schema to include new require fields and additional properties**:
* Add `"rrid"`, `"living_donor"`, `"bmi"`, `"diabetes_status"`, and `"diabetes_status_description"` to the require fields list.
  * Add new fields:
    * `bmi`: A `number` field.
    * `diabetes_status`: An `array` field of `strings` link to `PhenotypeTerm`.
    * `diabetes_status_description`: A `string` field with an `enum` of `"diabetic"`, `"non-diabetic"`, `"unspecified"`.
    * `hba1c`: A `number` field.
    * `diabetes_status_hba1c`: A `string` field with an `enum` of `"diabetic"`, `"non-diabetic"`, `"unspecified"`.
    * `living_donor`: A `boolean` field.
    * `pancreas_tissue_available`: A `boolean` field.
    * `center_donor_id`: A `string` field.
    * `biological_sex`: A `string` field with an `enum` of `"male"`, `"female"`, `"unspecified"`.
    * `donation_type`: A `string` field with an `enum` of `"DCD"`, `"NDD"`, `"MAID"`.
    * `cause_of_death`: A `string` field.
    * `c_peptide`: A `number` field.
    * `aab_gada`: A `boolean` field.
    * `aab_gada_value`: A `number` field.
    * `aab_ia2`: A `boolean` field.
    * `aab_ia2_value`: A `number` field.
    * `aab_znt8`: A `boolean` field.
    * `aab_znt8_value`: A `number` field.
    * `hla_typing`: An `array` field representing HLA typing.
    * `other_tissues_available`: An `array` field linked to `SampleTerm`.
    * `hospital_stay`: A `number` field.
  * Change `ethnicities` field title from `"Ethnicity"` to `"Self Reported Ethnicity"`.
  * Update `schema_version` from `"13"` to `"14"`.
  
### Minor changes since schema version 13

* Update calculation of `summary`.
* Extend `collections` enum list to include `Vista`.
* Extend `collections` enum list to include `IGVF_catalog_beta_v0.2`.
* Extend `collections` enum list to include `IGVF_catalog_beta_v0.3`.
* Extend `collections` enum list to include `IGVF_catalog_beta_v0.4`.

### Schema version 13

* Require `release_timestamp` for any objects with `released`, `archived`, or `revoked` status.

### Minor changes since schema version 12

* Update `aliases` regex to add `buenrostro-bernstein` as a namespace.
* Add `release_timestamp`.
* Add `MPRAbase` to `collections`.

### Schema version 12

* Disallow empty strings in `description`.

### Minor changes since schema version 11
* Expand `collections` enum list to include `ClinGen`, `GREGoR`, `IGVF_catalog_beta_v0.1`, and `MaveDB`.

### Schema version 11

* Rename `references` to `publication_identifiers`.

### Schema version 10

* Rename `human_donor_identifier` to `human_donor_identifiers`.

### Schema version 9

* Add `virtual`.

### Minor changes since schema version 8

* Add `human_donor_identifier`.

### Schema version 8

* Add `related_donors`.
* Remove `parents`.

### Minor changes since schema version 7

* Add `dbxrefs`.

### Schema version 7

* Remove `traits`.

### Schema version 6

* Remove `external_resource`.

### Minor changes since schema version 4

* Add `African Caribbean`, `Colombian`, `Dai Chinese`, `Kinh Vietnamese`, `Puerto Rican` to `ethnicities`.

### Schema version 4

* Rename `ethnicity` to `ethnicities`.

### Schema version 3

* Remove `health_status_history`.
* Add `phenotypic_features`.

### Minor changes since schema version 2

* Add `description`.
* Add `Pacific Islander` to `ethnicity` enum.
* Add `revoke_detail`.

### Schema version 2

* Restrict `parents`, `external_resources`, `aliases`, `collections`, `alternate_accessions`, `documents`, and `references` to be a non-empty array with at least one item.

### Minor changes since schema version 1

* Add `traits`.
* Rename `organism` to `taxa`.
* Require `sex`, set default to:
    ```json
    "unspecified"
    ```
* Rename `taxon_id` to `organism`.
* Restrict `taxon_id` to NCBI taxonomy ids that start with NCBI:txid followed by numbers.
