## Changelog for *`lab.json`*

### Minor changes since schema version 3

* Add `consortium_name` for labs that do not have a single Principal Investigator.
* `pi` is no longer required on its own; either `pi` or `consortium_name` must be specified.
* Update calculation of `title` to use `consortium_name` when `pi` is not specified.
* Update calculation of `summary`.
* Update `aliases` regex to add `buenrostro-bernstein` as a namespace.

### Schema version 3

* Disallow empty strings in `description`.

### Minor changes since schema version 2

* Add `description`.
* Add `aliases` to `identifyingProperties`.

### Schema version 2

* Restrict `aliases` and `awards` to be a non-empty array with at least one item.

### Minor changes since schema version 1

* Add `submitter_comment`, `submitted_by`, `creation_timestamp` and `aliases`.
