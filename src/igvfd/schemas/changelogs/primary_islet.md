## Changelog for *`primary_islet.json`*

### Minor changes since schema version 21
* Add calculated properties `purity_value` (max numeric from `purity[]`) and
  `post_shipment_viability` (quantitative with fallback to `post_shipment_islet_viability`).
* Search facets added for `isolation_center`, `organ_source`, `islet_function_available`,
  and nested `donors.diabetes_status_description`, `donors.age_group`, `donors.aab_positive`.
* Biosample donor embed frame expanded to include donor clinical/calc fields used for filters.

### Schema version 21

* Change `shipping_temperature` from `number` to `string` so values can be submitted as a single temperature or a range (e.g., `6-10`). Existing numeric values are converted to strings during upgrade.

### Minor changes since schema version 20

* Make `cold_ischaemia_time` optional (removed from `required`; added to `desired`).

### Schema version 20

### Minor changes since schema version 19

* Remove `islets_shipped` (moved to `measurement_set`).
* Added resource

### Schema version 19
