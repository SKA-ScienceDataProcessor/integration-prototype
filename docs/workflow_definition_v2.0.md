# SIP workflow definition, version 2.0

## Introduction

In order for the SIP Execution Control to be able to accept and execute
a requested Processing Block, the workflow associated with the
Processing Block must be known to the Execution Control runtime system.
For this to be the case, a workflow definition, which describes how the
workflow should be configured and run, must be registered in the
Execution Control Database.

This document describes the SIP workflow definition format required to
register workflows with the SIP Execution Control runtime system.

Once a workflow definition has been written, it can be registered with
the Configuration Database using a command line utility installed as
part of the `skasip-config-db` Python package (`pip install
skasip-config-db`) as follows:

```bash
skasip_config_db_register_workflows [path]
```

where `[path]` is a path containing one or more SIP workflow definitions
files and workflow stage configuration sub-folders.

In order to list the workflows currently registered with the system use
the following command:

```bash
skasip_config_db_workflow_definitions
```


## Concepts

A SIP workflow is a Directed Acyclic Graph (DAG) where the vertices or nodes are
called workflow stages and edges represent the ordering of stage execution.
Workflows can range from a single stage, to a complex set of sequential and
parallel stages.

Workflows are defined by a workflow definition file. This is a JSON or YAML
file which specifies the stages that make up the workflow, the order stages
should be executed, and additional meta-data such as resources required to
consider the workflow stage for execution.

Workflow stages, from which workflows are constructed, are each defined by a
set of files found in a stage configuration directory. This is a directory
named after the stage identifier found in the workflow definition and
contains a set of files which are used to specify how the stage should be
configured and executed.

When registering a workflow, the information in the workflow definition file
is combined with the stage configuration directories (for stages the
workflow depends on) in order to build a complete description of the workflow.
This complete description is stored in the Configuration Database and is
used each time the workflow is requested for execution.


## Workflow definition file

This is a YAML or JSON file whose filename must uniquely identify the
workflow. It is strongly recommended that this filename consists of a short
descriptive name followed by a version number, i.e. `vis-ingest-1.0.0.yml`.
To allow workflows to be configured by TM, workflow definition files
support [Jinja2](http://jinja.pocoo.org/docs/2.10/) template language
(see section below on [use of templates](#use-of-templates)).


### Top level structure

Workflow definition files are **required** to have two top level keys:

- `schema_version`: Currently has to be `2.0`
- `stages`: A list of dictionaries, where each dictionary in the
  list defines a stage in the workflow.


Examples:
```yaml
schema_version: '2.0'
stages: []
```

```json
{
  "schema_version": "2.0",
  "stages": []
}
```

### Workflow stages

Each stage dictionary in the `stages` list is has the following keys:

- `id`: (Required) The stage identifier / name.
- `version`: (Required) The stage version.
- `type`: (Required, not currently used) The type of stage.
  One of: Setup, Processing, Cleanup, Simulator, and Emulator.
- `timeout`: The maximum time the workflow stage is allowed to run for.
- `resources_required`: (Required, not currently used) List of resource
  dictionaries each of which define a resources required to be available in
  order for the workflow stage to begin execution.
- `dependencies`: (Optional) List of dependencies that must be satisfied
  before the stage can be executed. If not defined the stage is assumed to have
  no dependencies.

#### Workflow stage: `resources_required`

Each dictionary in the `resources_required` list specifies a resource required
by the workflow stage. In order for the workflow stage to execute, all resources
specified must be available. Each resource contain a `type` field which
identifies the type of resource. Other fields in the resource dictionary will
depend on the resource type as are as yet **TBD**.

Currently allowed resource types are:

- `nodes`
- `cpu`
- `memory`
- `buffer`

##### Resource type: `nodes`

As an example, for the resource of `type == nodes`, the following fields are
supported:

- `number`: (Required) The number of nodes.
- `flavour`: (Required) The flavour or type of node
- `exclusive`: (Required) Bool flag specifying if the workflow stage
  application requires exclusive access to the node.
- `label`: (Optional) The Docker Swarm node label for the nodes.

Note it is possible for multiple resource entries to be of the same type.
This allows for the possibility to for example require multiple types of
nodes to be available as a resource for a workflow stage.


#### Workflow stage: `dependencies`

Each entry in the `dependencies` list is a dictionary with the following keys:

- `type`: The type of dependency. One of: stage, buffer_object
- `value`: The value of the dependency. If depending on a stage, this would
  be the `id` of the stage this stage depend on.
- `condition`: The condition on the value that must be met. If
  depending on another stage, this is the state of the stage being depended
  upon needed for this stage to start execution; ie conditions could be
  `complete`, `running`, `aborted` etc.

### Examples

A simple YAML workflow definition:

```yaml
schema_version: 2.0
stages:
  - id: my_setup_stage
    version: 1.0.0
    type: setup
    timeout: 60s
    resources:
      - type: cpu
        value: 0.1
  - id: my_processing_stage
    version: 1.0.0
    type: processing
    timeout: 60s
    dependencies:
      - type: stage
        value: stage-01
        condition: complete
    resources:
      - type: nodes
        flavour: compute_a
        number: 10
        exclusive: true
```

This can also be specified in JSON as follows:

```json
{
  "schema_version": "2.0",
  "stages": [
  {
    "id": "my_setup_stage",
    "version": "1.0.0",
    "type": "setup",
    "timeout": "60s",
    "resources": [
    {
      "type": "cpu",
      "value": 0.1
    }
    ]
  },
  {
    "id": "my_processing_stage",
    "version": "1.0.0",
    "type": "processing",
    "timout": "20m",
    "resources": [
    {
      "type": "nodes",
      "number": 10,
      "flavour": "compute_a",
      "exclusive": true
    }
    ]
  }
  ]
}
```
Workflow definition files may also include Jinja2 templates. This allows
parameters, specified in the configured Processing Block, to modify the
workflow.

For example, the following workflow definition is modified by the template
parameters `{{ processing_timeout }}` and `{{ num_nodes }}`:

```yaml
schema_version: 2.0
stages:
    - id: stage-a
      version: 1.0.0
      type: setup
      timeout: 30s
      resources:
        - type: cpu
          value: 0.5
    - id: stage-b
      version: 1.0.0
      type: processing
      timeout: {{ processing_timeout }}
      dependencies:
        - type: stage
          value: stage-a
          condition: complete
      resources:
        - type: node
          flavour: compute_a
          number: {{ num_nodes }}
          exclusive: true
```

This is provided in the Processing Block configuration as follows (for more
details please refer to the Scheduling Block Instance (SBI) configuration
specification document):

```json
{
  "workflow": {
    "id": "...",
    "parameters": {
      "processing_timeout": "20s",
      "num_nodes": 10
    }
  }
}
```


## Stage configuration directories

The configuration for each stage is contained within a directory tree with the
following structure:

```bash
stages/<stage id>/<stage version>
```

where `<stage id>` and `<stage version>` must match the stage `id` and
`version` fields specified in the workflow stage definition file.

The stage directory contains set of files which define how the stage should
executed and configured. These are described below:

Note that workflow stages are (currently) executed as a set of Docker Services
using Docker Swarm. This may be extended in the future and if so, additional
files supporting this will be added to the list below.

Currently workflow stages are specified by the following files (each
described in more detail below):

- `docker_compose.yaml[.j2]` (Required) Defines how the stage is executed
  using Docker Compose format. This can be optionally extended using
  Jinja2 templating.
- `parameters<.json|.yaml>` (optional) JSON or YAML file which define a set
  of workflow stage parameters along with default values (where applicable).
- `args<.json|.yaml>[.j2]` (optional) Specialised parameter file
  which defines command line arguments that can be passed to workflow stage
  applications (services). When rendering `docker_compose` file templates,
  the contents of this file is provided to the template as the `args` variable.
  This file has no prescribed structure and is instead left to the individual
  workflow stage. This file can be optionally extended or modified using Jinja2
  templates using template variables defined in the parameters file (above).

### `docker_compose.yaml[.j2]`

SIP executes workflow stages using Docker Swarm. Because of this workflow
stages take advantage of the Docker Compose format file to specify what
Docker services should be started to execute the workflow stage. Due to the
limitations of static compose files, if required, this can be extended using
Jinja2 templating.

### `parameters<.json|.yaml>`

Workflow stages may be modified by a set of parameters specified when the
workflow is configured (in the SBI config). This JSON or YAML file defines any
parameters which can be used to modify the workflow stage.

The schema for this file is still **TBD**, for now a simple dictionary is
assumed where values, if specified are treated as defaults and where empty
are treated as parameters with no default that must be specified when
configuring the workflow or by the output of a previous workflow stage.


### `args.<.json|.yaml>[.j2]`

SIP supports the case where workflow stage applications are provided with
command line arguments in the form of a JSON or YAML string. This file
gives a mechanism to define these command line arguments in a templated
(in Jinja2), structured format which is loaded when registering the workflow
and where template parameters in the file are resolved prior to passing
arguments to workflow applications.

The contents of the file are loaded as a special parameters entry called
`args`, which is made available when rendering the `docker_compose.yaml.j2`
template. The structure of the file is very much workflow stage specific;
for example, where a workflow stage consists of multiple workflow stage
applications (or services), it is likely that the args file will
have a top level structure which maps arguments onto individual applications
or services.

## Use of templates

Workflow definitions, compose files and command line argument files (defined
in the section above) support [Jinja2](http://jinja.pocoo.org/docs/2.10)
template expansion.

Templates are rendered using template variables which are keys defined
in a data structure mapped to parameters specified in the workflow stage
parameters files that make up the workflow.

Internally each workflow stage gets a copy of all parameters defined in the
SBI config and workflow definition and these are made available to the
template when it is rendered with the same structure as that defined in the
JSON or YAML parameters specification, whether that is in the workflow
stage specification, workflow definition or SBI workflow configuration.

## Notes

- Workflow definition files may in future be specifiable through a script
  instead of or in addition to temperated a YAML or JSON format. If this
  becomes the case a workflow definition API will be provided.
- An additional top level key workflow definition file key, `parameters`,
  is reserved for future use. This would allow the workflow definition
  to statically override workflow stage parameters.
