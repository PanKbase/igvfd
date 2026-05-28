## Changelog for *`primary_islet.json`*

### Schema version 21

* Change `shipping_temperature` from `number` to `string` so values can be submitted as a single temperature or a range (e.g., `6-10`). Existing numeric values are converted to strings during upgrade.

### Minor changes since schema version 20

* Make `cold_ischaemia_time` optional (removed from `required`; added to `desired`).

### Schema version 20

### Minor changes since schema version 19

* Remove `islets_shipped` (moved to `measurement_set`).
* Added resource

### Schema version 19
