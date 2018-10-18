# SIP Master Controller Service (REST variant)

Previously master\_controller/mock\_watchdog

## Resources (in DB)
* __W__ Current state of SDP
* __R__ Target (commanded SDP state [target_state in mock\_watchdog])
* __W__ Target state of component *NAME* (component specific
state - e.g. tell processing controller to stop processing)
* __R__ Current state of components (services)
    * _NOTE:_ Initial implementation of 1 or 2 of the following from the EC:
        1. Processing Controller (Scheduler) - includes wrapped up state of processing block controllers
        1. Monitoring & logging services(s)

## Activities
* Update state of SDP
* Update component target states
* Update current state of components (services)

## Other Activities
* Interrogate the state of components

## Usage
Ultimately this will be run within a docker container along with the
Master Interface Service (either the RESTful or the TANGO variant),
and a REDIS database,
each in their own container.
However it will also be useful for testing and debugging purposes to be 
able to run
the service standalone. Instructions are here for both.

### Run in Docker containers

#### Standalone Docker container
(Still under construction)

Follow these commands within this directory unless otherwise stated.
1. Get a copy of the config_db library. 
If the file config_db.zip does
not appear in this directory copy it from _../configuration__db/redis_.
If it does not appear in that directory run the 
following commands to create it:
```bash
cd ../configuration_db/redis
zip -r config_db.zip setup.py config_db
cp config_db.zip ~-
cd -
```
1. Build a Docker Image.
```bash
docker build -t rest_component .
```
1. Run the image in a container

#### With REST variant Master Interface Service
Run the __start_master_controller_service__ script which can be found
in the ``../master_interface_service/rest`` directory.
This script should be run from that directory and will not run properly
if it is not.

#### With TANGO variant Master Interface Service
There is no TANGO variant in this branch.

### Stop the Docker containers
Run the __stop_master_controller_service__ script which can be found
in the ``../master_interface_service/rest`` directory.

### Run standalone
As the application is written in Python certain packages, including the 
__config_db__ package, need to be installed. 
It is therefore recommended that a Python Virtual Environment (__venv__)
be used.
As the requirements for this application are a subset of those for the
REST application you _could_ share the same __venv__ for both 
applications, in which case you should change to that directory and follow 
the instruction there; and with an activated __venv__ come back
to this directory and run
```
python3 -m app
```
The following instructions are for creating a __venv__ specifially
for this application in this directory:

1. Create a Virtual Environment: `python3 -m venv venv`
2. Activate it: `. venv/bin/activate`
   * this sets your path and other environment varables to find 
   utilities and libraries in the __venv__
3. upgrade pip: `pip install --upgrade pip`
   * Not required; however it will stop pip from reporting a later version 
   is available
4. Install the required packages: `pip install -r requirements.txt`
   * A file, `requirements.txt` contains a list of packages to be installed
5. Install Nijin's config_db package: `pip install ../configuration_db/redis`

Each line below corresponds to the instruction above:
```
$ python3 -m venv venv
$ . venv/bin/activate
(venv)$ pip install --upgrade pip
(venv)$ pip install -r requirements.txt
(venv)$ pip install ../configuration_db/redis
```
It is now possible to run:
```
(venv)$ python3 -m app
```
It is possible to run the application from the __venv__ without activating
the __venv__:
```
$ venv/bin/python3 -m app
```
