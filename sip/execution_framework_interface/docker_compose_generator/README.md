# Docker Compose generator library

Library for generating Docker Compose format files for use with Docker Swarm
based on jinja2 templates.

## Quick-start

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

```bash
py.test --pylint --codestyle -s -v --pylint-rcfile=../../../.pylintrc .
```