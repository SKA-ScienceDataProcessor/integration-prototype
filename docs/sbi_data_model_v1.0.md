# Configuration Database Scheduling Block Instance Data Model, v1.0

This document describes the physical data model for Scheduling Block Instances
(SBIs) stored in the Execution Control Configuration Database.

## Primary Key

Scheduling Block instances are stored at a key in the database with a `sbi:`
prefix, followed by the Scheduling Block Instance identifier. For example, for a
Scheduling Block Instance with `id == SBI-20190122-test-001` the database key
will be:

```
sbi:SBI-20190122-test-001
```

## Scheduling Block Instance fields

- `id`: (string) The SBI identifier.
- `version`: (string) The version of the SBI.
- `status`: (string) The status of the SBI.
- `updated`: (string) When the SBI was last updated. datetime ISO 8601 UTC.
- `created`: (string) When the SBI was first created. datetime ISO 8601 UTC.
- `processing_block_ids`: (List) Processing Block identifiers
- `subarray_id`: (string) Subarray identifier or None.
- `scheduling_block`: (Hash) Scheduling block data object.


## Scheduling Block Instance sub-keys

Stored with a key using the pattern `<primary_key>:<sub-key>` where
`<primary-key>` is the Primary Key of the SBI as defined above, and <sub-key>`
is one of:

- `events_list`: (List) List of events identifiers associated with this SBI
- `events_data`: (Hash) Event data for each event associated with this SBI with
  data entries mapped to the the event identifier.

## Scheduling Block data object

This is a JSON string with the following keys:

- `id`: (string) The Scheduling Block identifier.
- `project`: (string) The Project identifier.
- `programme_block`: (string): The programme block identifier.
