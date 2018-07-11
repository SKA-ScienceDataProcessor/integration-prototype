# Docker Compose generator library

Library for generating
[Docker Compose](https://docs.docker.com/compose/compose-file/) files
for use with Docker Swarm based on workflow stage configuration data
and [Jinja2](http://jinja.pocoo.org/docs/2.10/) templates.

This library is intended to be used when executing Processing Block workflow
stages from Processing Block Controller when Docker Swarm is used
to deploy the runtime containers via the SIP Docker Swarm Python API which
operates using the Docker compose format to define services and their
configuration. This has been chosen to not have to invent a new way of
specifiying services and allows a programatic API with the equivalent function
of the `docker stack deploy` Docker CLI function.

This library assumes that the workflow stage configuration adheres to the
data model described on SDP confluence at
<https://confluence.ska-sdp.org/display/WBS/SIP%3A+Configuration+Database+Data+Model>.

In this model each workflow stage is an object of a well defined type and
a set of conifuration objects describing the resource requirements,
execution engine configuration and workflow application configuration.
According to the specified type, this library parses these configuration
objects to generate a Docker compose file format string which can be
saved or passed to the SIP Docker Swarm Python API.

## Quick-start

In order to use the library, import the `compose_generator` module and call the
`generate_compose_file` method which takes a workflow stage configuration
dictionary described by the SIP workflow stage configuration data model.

This function returns a string containing a Docker Compose file which can
be used to run the workflow stage.

Currently this library handles the following types of workflow stage:

- vis_ingest
- csp_vis_emulator

In order to add additional workflow stage types, a new module should be added
to the `generators` folder which includes a function that interprets the
workflow stage configuration and generates a Docker Compose file. How this
function is written will be dependenent on the workflow type but may make
use of templates and static configuration files loaded from a data store.
Once the new generator module and function has been added it should also be
added to the set of if statement in the `compose_generator.py`
`generate_compose_file` method which handle each workflow stage type.

## Running the linter and unit tests

Linting and unit tests are run automatically by the SIP CI/CD system but can
also be run manually from the `docker_compose_generator` code directory with:

```bash
py.test --pylint --codestyle -s -v --pylint-rcfile=../../../.pylintrc .
```
