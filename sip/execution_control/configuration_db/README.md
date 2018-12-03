# SIP Configuration Service

## Introduction

The Configuration Database is a backing service for use by SKA SIP Execution
Control (EC) and Tango Control components. This package contains a library 
providing specialised functions for interfacing with data objects in the 
EC Configuration Database.

For a description of the Data Model used by this library see Sections 7.4.4 
and 7.5.6 of the SIP Report.

This library provides modules for each of the data objects stored within
the EC configuration database. These are built on top of a simple low-level 
wrapper to the [Python Redis API](https://redis-py.readthedocs.io/en/latest/),
which handles connections to the database and abstraction from the Python
Redis API.

## Installation

This library can be installed using `pip` with the following command: 

```bash
pip install -U skasip-config-db
```

## Usage

Example usage:

```python
# coding: utf-8
"""Example usage."""
from sip_config_db.scheduling import Subarray, SchedulingBlockInstance
from sip_config_db.states import SDPState
from sip_config_db.utils.generate_sbi_config import generate_sbi_config

sdp_state = SDPState()
print(sdp_state.current_state)

subarray = Subarray(0)
subarray.activate()
print(subarray.active)

sbi_config = generate_sbi_config(register_workflows=True)
sbi = SchedulingBlockInstance.from_config(sbi_config)
print(sbi.id)
```

## Utility Scripts

The package installs a number of utility scripts, described below:

#### Initialise the database.

`skasip_config_db_init [--data-path=PATH]`

Can be used to initialise the configuration database. The optional 
`--data-path=PATH` argument, can be used to defined a custom 
path containing the initial set of SDP services and workflows used to
initialise the database. If specifying `--data-path`, and the specified `PATH`
does not exist a copy of the default data pat will be created at the specified
path.

#### Register workflows

Register workflows from the specified workflow path.

```bash
skasip_config_db_register_workflows [workflow path]
```

#### Add an SBI to the database

Adds an SBI to the database.

```bash
skasip_config_db_add_sbi [--subarray N] [--activate] [--help]
```

#### Generate an SBI JSON configuration

Generate an SBI JSON configuration.

```bash
skasip_config_db_sbi_json
```

#### Update the current state

Updates the current state of SDP or a specified service.

```bash
skasip_config_db_update_state [--service SUBSYSTEM.NAME.VERSION] [--help] new_state
```

#### List workflow definitions

List known workflow definitions.

```bash
skasip_config_db_workflow_definitions
```

## Running tests

Unit tests are run automatically the 
[SIP CI/CD service](https://travis-ci.com/SKA-ScienceDataProcessor/integration-prototype).
It is also possible to run them manually with the following commands from the
root SIP:

***Note**: a Redis db container must be started first in order for most of
these tests to pass (See below)*

```bash
virtualenv -p python3 venv
source venv/bin/activate
pip install -r testing_requirements.txt
pip install -r sip/execution_control/configuration_db/requirements.txt
python3 -m pytest --pylint --codestyle --docstyle -s -v \
    --pylint-rcfile=.pylintrc --rootdir=. \
    sip/execution_control/configuration_db
```

## Starting Configuration Database Redis containers.

To start Docker containers for a Redis Db instance (with a persistent volume)
as well as a [Redis Commander](https://github.com/joeferner/redis-commander)
instance (useful for debugging) issue the following command:

```bash
docker stack deploy -c docker-compose.yml [stack name]
```

Once finished, to clean up.

```bash
docker stack rm [stack name]
```

It is also possible to run redis server natively (without Docker) with:

```bash
redis-server
```

