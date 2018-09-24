# SIP Configuration Service (Redis variant)

## Roles and responsibilities

The SIP Execution Control Configuration Database Service provides a 
[backing service](https://12factor.net/backing-services) for storing data used
by the different Execution Control Service components. It also currently 
provides limited event queue like capability for communicating events
between the Processing Controller Interface service and Scheduler. 

The choice of database technology used by this service, currently Redis, 
is hidden from other Execution Control Services by means of a configuration 
database client library API. This library is written as a set of Python 
modules which are structured such that there is a low level abstraction 
layer on top of the database's 
[Python API](https://redis-py.readthedocs.io/en/latest/) and a set of higher 
level modules providing which provide a view of configuration in terms of a set
of resources targeted at the the various Execution Control Services which 
depend on this library.

Design notes for this service can be found in the
[SIP Execution Control Confluence pages](https://confluence.ska-sdp.org/display/WBS/SIP%3A+%5BEC%5D+Configuration+Database+Service)

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

### Package the client

Following instructions shows have to package the client

Go to `sip/execution_control/configuration_db/redis` folder:

```bash
python3 setup.py develop
pip install .
```

You should now be able to run the db_client anywhere in the system. 
e.g.

```python
import db_client
db_client.MasterDbClient()
```


### Utility Scripts

To set initial data into the configuration database run the following command:

```bash
python3 -m db_client.utils.set_initial_data
```

### Test Scripts

<<<<<<< HEAD

While unit tests are run automatically the 
[SIP CI/CD service](https://travis-ci.com/SKA-ScienceDataProcessor/integration-prototype),
it is possible to run them manually with the following command from the
`sip/execution_control/configuration_db/redis` folder:

***Note**: a Redis db container must be started first in order for most of
these tests to pass*

```bash
virtualenv -p python3 venv
source venv/bin/activate
pip install pytest
pip install pytest-codestyle
pip install pytest-pylint
pip install pytest-docstyle
pip install -r requirements.txt

```bash
pytest --pylint --codestyle --docstyle -s -v --pylint-rcfile=../../../../.pylintrc .
=======

While unit tests are run automatically the 
[SIP CI/CD service](https://travis-ci.com/SKA-ScienceDataProcessor/integration-prototype),
it is possible to run them manually with the following command from the
`sip/execution_control/configuration_db/redis` folder:

***Note**: a Redis db container must be started first in order for most of
these tests to pass*

```bash
virtualenv -p python3 venv
source venv/bin/activate
pip install pytest
pip install pytest-codestyle
pip install pytest-pylint
pip install pytest-docstyle
pip install -r requirements.txt
```

Install the client as package. Follow "Package the client" instruction.

```bash
pytest --pylint --codestyle --docstyle -s -v --pylint-rcfile=../../../../.pylintrc 
>>>>>>> 9f548dce585590aaf18690089851b3a85b982d46
```
