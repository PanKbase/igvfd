## Changelog for *`human_beta_cell_line.json`*

### Schema version 1

* Initial schema creation for Human Beta Cell Line biosample.
* Add required fields: `award`, `lab`, `sources`, `donors`, `sample_terms`, `sample_name`, `classifications`, and `description`.
* Add cell line-specific fields: `sample_name`, `classifications`, `passage_number`, `growth_medium`, `date_harvested`, `authentication`, `file_sets`.
* Add relationship fields: `parts`, `pooled_in`, `demultiplexed_to`, `multiplexed_in`, `sorted_fractions`.
* Inherit standard biosample properties through mixins including age fields, treatments, modifications, and biomarkers.
* Add dependent schema requiring `growth_medium` when `passage_number` is specified.
* Restrict `taxa` to "Homo sapiens" only.
* Set `classifications` to only accept "cell line" enum value for schema compatibility.