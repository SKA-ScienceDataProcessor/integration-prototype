# Configuration Database Processing Block Data Model, v1.0

This document describes the physical data model for Processing Blocks (PBs)
stored in the Execution Control Configuration Database.

## Primary Key

Processing Blocks (PBs) are stored at a key in the database with a `pb:` prefix,
followed by the Processing Block identifier. For example, the database key for
a PB with `id` `PB-20190122-test-001` will be `pb:PB-20190122-test-001`.

## Processing Block fields

Each PB is stored as a Redis Hash with the following fields:

1. `id`**: The Processing Block identifier
2. `version`: Data model version (same as the SBI data model / schema version)
3. `sbi_id`**: The (parent) SBI identifier.
4. `type`**: Type of Processing block. One of: `offline` or `realtime`
5. `status`: The Processing Block status
6. `created`: Processing Block creation datetime, ISO8601 UTC datetime
7. `updated`: Processing Block last updated datetime, ISO8601 UTC datetime
8. `priority`: The scheduling priority of the PB.
9. `dependencies`**: List of dependencies for the processing block.
10. `workflow_id`**: The workflow identifier
11. `workflow_version`**: The workflow version
12. `workflow_stages`: List of workflow stage configuration
13. `workflow_parameters`: Hash of workflow parameters.

Fields marked with '**' are obtained from the SBI configuration. The
`workflow_stages` field a copy of the of the workflow stages specified
by the workflow definition stored in the database at the key
`workflow_definition:<workflow_id>:<workflow_version>:stages`. A copy is made
to allow for template modification of workflow stages based on parameters
local to the specific PB.

##  Workflow Stage fields

Each 'workflow stage' entry with the PB's `workflow_stages` field is an object
(stored as a JSON string) with the following fields:

1. `id`**: The workflow stage identifier
2. `version`**: The workflow stage version
3. `type`**: The workflow stage type
4. `status`: The workflow stage status
5. `timeout`**: The maximum allowed execution time for the workflow stage
6. `resources_required`**: Resources required by the workflow stage
7. `resources_assigned`: Resources assigned to the workflow stage
8. `updated`: Last updated datetime, ISO8601 UTC datetime
9. `parameters`**: Workflow stage parameters
10. `dependencies`**: Workflow stage dependencies
11. `args`**: Workflow stage application arguments
12. `compose_file`**: Compose file string

Fields marked with '**' are obtained directly from the workflow definition.

## Processing Block sub-keys

Stored with a key using the pattern `<primary_key>:<sub-key>` where
`<primary-key>` is the Primary Key of the SBI as defined above, and <sub-key>`
is one of:

1. `events_list`: (List) List of events identifiers associated with this PB
1. `events_data`: (Hash) Event data for each event associated with this PB with
  data entries mapped to the the event identifier.

## Additional meta-data keys

The following keys contain list of PB identifiers organised by status. While
this duplicates data in the PB data object status fields, it provides a more
convenient way to query status of all known PBs.

- `pb:active`
- ...

## Notes

- How parameters are combined still requires some consideration and is therefore
  likely to change.
- Currently workflow stage parameters are defined as part of the workflow stage
  definition. This defines optional and required parameters for each workflow
  stage, along with (optional) defaults. Parameters can then be set by values
  specified in the SBI and/or other workflow stages completed earlier in the
  workflow graph.
- It is possible that parameters can or should be defined at both the workflow
  stage and PB level. While ultimately (prior to execution in the Processing
  Block Controller) parameters will be needed at the stage level, it is likely
  that some parameters may be shared between stages and therefore better be
  described as processing block level parameters.
