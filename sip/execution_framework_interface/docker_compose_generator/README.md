# Docker Compose generator library

Library for generating
[Docker Compose](https://docs.docker.com/compose/compose-file/) format files
for use with Docker Swarm based on [Jinja2](http://jinja.pocoo.org/docs/2.10/)
templates.

This is intended to be used when executing Processing Block workflow stages
by the Processing Controller (Scheduler) and / or Processing Block Controller
when the SIP Docker Swarm Python API is being used. The SIP Docker Swarm
Python client API uses Docker Compose format files in order to run
Docker Services on a Swarm Cluster providing an API equivialent to the
`docker stack deploy` command. This library can be used to dynamically
create the Docker Compose files based on Jinja2 templates and Processing Block
workflow configuration information.

## Quick-start

**TODO(BM) Move this quickstart info somewhere else as is more about testing
a docker compose example that the final end product of this library.?**

To test the 'generated' recevive compose file

```bash
docker stack deploy -c vis_receive_example.yml <stack name>
```

This should generate a recv servive which can be inspected with:

```bash
docker service ls
```

or:

```bash
docker stack services <stack name>
```

To check what stacks are running:

```bash
docker stack ls
```

To remove the stack (and its services ... and the service containers)

```bash
stack stack rm <stack name>
```

## Running the linter and unit tests

Linting and unit tests are run automatically by the SIP CI/CD system but can
also be run manually from the `docker_compose_generator` code directory with:

```bash
py.test --pylint --codestyle -s -v --pylint-rcfile=../../../.pylintrc .
```
