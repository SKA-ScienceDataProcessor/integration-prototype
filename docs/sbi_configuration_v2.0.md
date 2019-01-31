# SIP Scheduling Block Instance (SBI) configuration, version 2.0

## SBI configuration

### Top-level structure

- `id`: the SBI identifier
- `version`: The SBI (schema) version, currently must be 1.1
- `scheduling_block`: Scheduling Block (SB) information data structure
- `processing_blocks`: List of Processing Blocks


### Scheduling Block (SB) structure

Placeholder for metadata linking the SBI to the parent SB.

- `id`: The SB identifier
- `project`: Project identifier, must be "sip",
- `programme_block`: Programme block identifier

### Processing Blocks (PB)

This is a list of Processing Block (PB) object data structures. Processing
Blocks defined the unit of work scheduled by SIP. Each PB has the following
keys:

- `id`: The PB identifier
- `type`: The PB type. One of 'offline' or 'realtime'
- `priority`: Scheduling priority
- `dependencies`: Dependencies on other PBs. SBIs or buffer data objects.
- `workflow`: The specification of the workflow to be used by the PB along with
  any parameters which configure the workflow.

### Processing Block Workflow structure

The workflow structure has the following keys:

- `id`: The workflow identifier
- `version`: The workflow version
- `parameters`: A structure / dictionary of parameters used to configure /
  modify the workflow. The structure of the `parameters` must match that defined
  for the workflow workflow (or workflow stages which the workflow is
  constructed)

## Example:

```json
{
  "id": "SBI-20190122-sip-test-001",
  "version": "2.0",
  "scheduling_block": {
    "id": "SB-20190122-sip-test-001",
    "project": "sip",
    "programme_block": "sip_tests"
  },
  "processing_blocks": [
  {
    "id": "PB-20190122-sip-test-001",
    "type": "offline",
    "priority": 1,
    "dependencies": [],
    "workflow": {
      "id": "my_workflow",
      "version": "1.0.0",
      "parameters": {
        "stage1": { "duration": "10s" },
        "stage2": { "duration": "20s" }
      }
    }
  }
  ]
}
```

## Notes

- Removed the the PB `version` key as it was decided that this was too closely
  linked to the SBI version to warrant a separate version.
- Removed the PB `resources_required` key as it was decided that this overlaps
  too much with the workflow stage resources.
