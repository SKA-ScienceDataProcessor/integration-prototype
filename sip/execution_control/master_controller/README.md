# SIP Master Controller Service

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
* Interrogate the state of components

## Usage
Ultimately this will be run within a Docker container and requires that the
SDP Master Interface Service (either the RESTful or the TANGO variant), 
and a REDIS database are also running (each in their own containers) for full
functionality. 

For testing and debugging purposes, to be it can be useful to run this service
outside of its Docker container. Instructions below describe both of these
options.

### Run using Docker

To start the containers required to run this service on Docker Swarm,
use the following command:

```bash
docker stack deploy -c docker-compose.yaml mc
```

To tear down the containers use the following command:

```bash
docker stack rm mc
```

To view logs from the Master Controller service container use the following
command:

```bash
docker service logs mc_master_controlller
```

The scripts `./scripts/deploy.sh`, `./scripts/tear_down.sh`, and 
`./scripts/show_logs.sh` are utility wrappers around these commands. 

#### Building the Docker image

A script is provided which will build the Docker image and upload it to 
Docker Hub. For the upload to succeed, you must be logged into a dockerhub 
account (which can be done with the command `docker login`), and be a member
of the `skasip` docker hub project.

```bash
./scripts/build_docker_image.sh
```

### Run natively (without Docker)

Once the required dependencies (specified in `requirements.txt`) are installed
the service can be started natively with the following command:

```bash
python3 -m app
```

To function a REDIS database instance will also need to have been started
and exposed either on `localhost` or on a host specified the `REDIS_HOST`
environment variable, and on either port `6379` or the port specified by
the environment variable `REDIS_PORT`.

Create and activate Python Virtual Environment and install package 
dependencies: 

1. Create the Virtual Environment: `python3 -m venv venv`
2. Activate it: `. venv/bin/activate`
   * this sets your path and other environment variables to find 
   utilities and libraries in the __venv__
3. Upgrade pip: `pip install --upgrade pip`
   * Not required; however it will stop pip from reporting a later version 
   is available
4. Install the required packages: `pip install -U -r requirements.txt`
   * A file, `requirements.txt` contains a list of packages to be installed

Each line below corresponds to the instruction above:
```
$ python3 -m venv venv
$ . venv/bin/activate
(venv)$ pip install --upgrade pip
(venv)$ pip install -U -r requirements.txt
```
It is now possible to run:
```
(venv)$ python3 -m app
```
