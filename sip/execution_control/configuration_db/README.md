# SIP Configuration Service (Redis variant)

## Introduction

The Configuration Database is a backing service for use by Execution
Control and Tango Control components. This package contains a library 
providing specialised functions for interfacing with the Configuration
Database at the abstraction of the Execution Control data objects.

For a description of the Data Model used by this library see Sections 7.4.4 
and 7.5.6 of the SIP Report.   

This library is written as a set of Python modules which are structured 
such that there is a low level abstraction layer on top of the database's 
[Python API](https://redis-py.readthedocs.io/en/latest/) `config_db_redis.py`
and a set of higher level classes providing interfaces to data objects
stored in the database.

## Quickstart

To start Docker containers for a Redis Db instance (with a persistent volume)
as well as a [Redis Commander](https://github.com/joeferner/redis-commander)
instance (useful for debugging) issue the following command:

```bash
docker-compose up -d
```

This will deploy the containers to the local Docker installation. If wanting
to deploy to Docker Swarm instead use the following command:

```bash
docker stack deploy -c docker-compose.yml [stack name]
```

Once finished, to stop this service and remove its running containers, if
started using `docker-compose` (with the local Docker engine) issue the
command:

```bash
docker-compose rm -s -f
```

or if using Docker Swarm mode:

```bash
docker stack rm [stack name]
```

It is also possible to run redis server natively (without Docker). This is
useful for development and debugging.

Start redis server

```bash
redis-server
```

Note - It requires redis to be installed and all python packages in the
requirements.txt file

### Installation using `pip`

This library can be installed using `pip` with the following command: 

```bash
pip install git+https://github.com/SKA-ScienceDataProcessor/integration-prototype@master#egg=config_db\&subdirectory=sip/execution_control/config_db
```

It can also be installed from a local copy of the code using:

```bash
pip install sip/execution_control/configuration/db
```

### Utility Scripts

To set initial data into the configuration database run the following command:

```bash
skasip_init_config_db [data_path]
```

### Running tests

While unit tests are run automatically the 
[SIP CI/CD service](https://travis-ci.com/SKA-ScienceDataProcessor/integration-prototype),
it is possible to run them manually with the following command from the
root sip code folder using the following commands:

***Note**: a Redis db container must be started first in order for most of
these tests to pass*

```bash
virtualenv -p python3 venv
source venv/bin/activate
pip install -r testing_requirements.txt
pip install -r sip/execution_control/configuration_db/requirements.txt
python3 -m pytest --pylint --codestyle --docstyle -s -v \
    --pylint-rcfile=.pylintrc --rootdir=. \
    sip/execution_control/configuration_db
```
