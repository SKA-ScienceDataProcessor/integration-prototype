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
(Still under construction)

Follow these commands within this directory unless otherwise stated.
1. Get a copy of the config_db library. 
If the file config_db.zip does
not appear in this directory copy it from _../../configuration__db/redis_.
If it does not appear in that directory run the 
following commands to create it:
```bash
cd ../../configuration_db/redis
zip -r config_db.zip setup.py config_db
cp config_db.zip ~-
cd -
```
1. Build a Docker Image.
```bash
docker build -t rest_component .
```
1. Run the image in a container
```bash
docker run -it -p5000:5000 -e5000 rest_component
```
Point a browser at __localhost:5000__

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
