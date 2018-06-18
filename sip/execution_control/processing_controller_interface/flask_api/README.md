# Processing Controller Interface (REST variant)

**Docker image:**
[`skasip/pci_flask`](https://hub.docker.com/r/skasip/pci_flask)

## Introduction

This service provides an external interface to SDP for controlling the list of
Scheduling Block Instances (and their associated Processing Blocks) registered
with the SDP system, in particular the SDP scheduler. This interface
provides this information in the form of a set of resources namely:

1. Scheduling Block Instance list
2. Scheduling Block Instance details
3. Processing Block list
4. Processing Block details
5. Sub-array list
6. Sub-array details

This service is backed by the Configuration Database service which is used
to store Scheduling Block Instance data structures, as well as to communicate
between this service and the Processing Controller Scheduler Service via
a simple event queue.

Interaction with the Configuration Database Service is performed via a
client API provided by the Configuration Database Service implementation.

Activities provided by these resources include:

1. Submitting a new Scheduling Block Instance to SDP
2. Query list of Scheduling Block Instances known to SDP
3. Query list of Scheduling Block Instances associated with a given sub-array
4. Query details of a Scheduling Block
5. Query list of Processing Blocks known to SDP
6. Query list of Processing Blocks associated with a given sub-array
7. Query details of a Processing Block

Design notes for this service can be found in the
[SIP Execution Control Confluence pages](https://confluence.ska-sdp.org/display/WBS/SIP%3A+%5BEC%5D+Processing+Controller+Interface+Service)

## Known issues

- Mapping of the JSON RESTful API presented by this Flask app to the
  baseline Tango Implementation.
- Handling of the sub-array interface(s). This could be required to have a
  time dimension currently completely ignored by this interface.

## Quick-start

The quickest way to get started with this service is to deploy the Docker
image and a Redis container, fulfilling the role of the Configuration Database,
using the provided [Docker Compose](https://docs.docker.com/compose/) file.

This can be deployed in two ways: Using a local Docker engine with
`docker-compose`, and to a Docker Swarm using `docker stack deploy` (see below).
Once started, the service will be available on port 5000 on the host where
the service was started (or in the case of Docker Swarm, port 5000 on
any leader node).

### Using `docker-compose`

To start the Processing Controller Interface service and a Redis Configuration
Database.

```bash
docker-compose up -d
```

To stop and tear down the services

```bash
docker-compose rm -s -f
```

### Using `docker stack deploy`

To deploy the Processing Controller Interface service and a Redis Configuration
Database as a Docker stack running on Docker Swarm:

```bash
docker stack deploy -c docker-compose.yml pci
```

To stop and tear down the services

```bash
docker stack rm pci
```

## Running the service during development

During development, it is often useful to be able to run the service
outside of Docker. There are a number of ways to do this, but in all cases
a Redis container fulfilling the role of the Configuration Database must be
created. This can be done one of the following methods:

1\. `docker-compose -f docker-compose.dev.yml up -d`

2\. `docker stack deploy -c docker-compose.dev.yml pci_dev`

Both of these options will start a Redis Database container along with a
Redis Commander web UI container to view the contents of the database.
The Redis Commander UI is published from the container on port `8081`.

Once the Configuration Database container has started, this service (the
Processing controller Inteface service) can be started as follows:

```bash
virtualenv -p python3 venv
source venv/bin/activate
pip install -r requirements.txt
export FLASK_APP=app/app.py
export FLASK_DEBUG=True
export SIP_PCI_LOG_LEVEL='DEBUG'
flask run --host=0.0.0.0 --port=5000
```

Once finished the commands `docker-compose rm -s -f` or
`docker stack rm pci_dev` can be used to stop and remove containers.

## Building the Docker image and publishing it to [hub.docker.com](https://hub.docker.com/u/skasip)

Tag the local image and push it to the hub.docker.com registry.
In order to do this you will need:

1. a hub.docker.com account
1. to be part of the [`skasip` organisation](https://hub.docker.com/u/skasip)
   on hub.docker.com
1. to be logged into your hub.docker.com account (eg. with the
   `docker login` command)

Once these steps are complete, in order to build and push any changes to
this the hub.docker.com registry use the following commands.

```bash
docker build -t skasip/pci_flask .
docker push skasip/pci_flask
```

## Utility Scripts

### Initialising the Configuration Database Service (for testing)

In order to provide a set of test data in the test Configuration Database
service a utility script is provided in the `utils` folder called `init_db.py`.

This will drop all existing data in the Configuration Database and replace
it with a set of randomly created Scheduling Block Instance data structures.

This can be run with the command:

```bash
python3 -m app.db.init [number of scheduling blocks, default==3]
```

## Testing

A number of unit tests are provided with this module. These assume that a
Redis Database container exists (see instructions above). Unit tests can then
be run with the following commands:

```bash
virtualenv -p python3 venv
source venv/bin/activate
pip install pytest
pip install pytest-codestyle
pip install pytest-pylint
pip install -r requirements.txt
export SIP_PCI_LOG_LEVEL='NOTSET'
py.test --pylint --codestyle -s -v --durations=3 --pylint-rcfile=../../../../.pylintrc .
```

Also note the linting and unit tests are also run on the SIP CI/CD system at
[Travis-CI](https://travis-ci.com/SKA-ScienceDataProcessor/integration-prototype)
every time a change is made to the code.