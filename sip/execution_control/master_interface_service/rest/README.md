# SIP Master Interface Service (REST variant)

Previously master\_controller

## Resources (in DB)
* __R__ Current SDP State
* __W__ Target (commanded) SDP state

## DB Activities
* Read current SDP state
* Read target state
* Set target (commanded) SDP state

## Other activities
* Compute Tango state


## Usage
Ultimately this will be run within a docker container along with the
Master Controller Service, and a REDIS database,
each in their own container.
However it will also be useful for testing and debugging purposes to be 
able to run
the service standalone. Instructions are here for both.

### Run in Docker containers

#### Standalone Docker container
(no instructions for now)

#### With Master Controller Service
Run the __start_master_controller_service__ script which can be found
in this directory.
This script should be run from this directory and will not run properly
if it is not.

### Stop the Docker containers
Run the __stop_master_controller_service__ script which can also be found
in this directory.

### Run standalone
As the application is written in Python certain packages, including the 
__config_db__ package, need to be installed. 
It is therefore recommended that a Python Virtual Environment (__venv__)
be used.

The following instructions are for creating a __venv__ 
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
5. Install Nijin's config_db package: `pip install ../../configuration_db/redis`

Each line below corresponds to the instruction above:
```
$ python3 -m venv venv
$ . venv/bin/activate
(venv)$ pip install --upgrade pip
(venv)$ pip install -r requirements.txt
(venv)$ pip install ../../configuration_db/redis
```
It is now possible to run:
```
(venv)$ gunicorn -b 0.0.0.0:5000 app.app:APP
```
It is possible to run the application from the __venv__ without activating
the __venv__:
```
$ venv/bin/gunicorn -b 0.0.0.0:5000 app.app:APP
```
