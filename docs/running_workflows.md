# Running workflows

Each workflow in SIP is associated with a Processing Block data structure and
run by an instance of the Processing Block Controller service.

The Processing Block Controller is a Celery worker whose code can be found in
the `sip/execution_control/processing_block_controller` directory.

In normal operation, workflows are scheduled by the Processing Controller
service, `sip/execution_control/processing_controller`, which watches for new
Processing Block objects entered into the Configuration Database by a Tango edge
device (The SDP Tango Master, or one of the SDP Subarray devices). Tango devices
create new Processing Block objects when they receive a Scheduling Block
Instance configure request (see `docs/sbi_configuration_v2.0.md`).

In order to successfully request that a workflow be considered for execution, a
workflow definition for the given workflow must be first registered with the
system. Registered workflows are found in the configuration database.

Workflows can be registered with the system using the following command:

```bash
skasip_config_db_register_workflows [path]
```

Where `path` contains a SIP workflow definition.

To list the workflows already registered with the system the following
command can be used:

```bash
skasip_config_db_workflow_definitions
```

In order to write a new workflow definition see
`docs/sip_workflow_definition_v2.0.md`.

