# Processing Controller Interface (REST variant)

## Roles and responsibilities

This service provides an external interface to SDP for interacting 
Scheduling Block Instances, the Processing Blocks they contain, and the 
associated Sub-Arrays known to SDP. This service is backed by the 
Configuration Database service which is both used to store Scheduling Block 
Instance data structures as well as to communicate between this service and the
Processing Controller Scheduler Service by means of a simple event queue.
Interaction with the Configuration Database Service is performed via a 
client API provided by the Configuration Database Service implementation.  

This interface exposes the following resources:

1. Scheduling Block Instance list
2. Scheduling Block Instance details
3. Processing Block list
4. Processing Block details
5. Sub-array list
6. Sub-array details

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


## Quickstart

To build the Docker Images needed to run this service use the following command:

```bash
docker-compose build
```

To start the Docker Containers needed to run this service during development on
a local Docker engine:

```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

This can also be run using Docker Swarm mode with the following command:

or 

```bash
docker stack deploy -c docker-compose.dev.yml [stack name]
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

It is also possible to run this service natively (without Docker) against the 
deployed development Configuration Database Service. This is very useful
for development and debugging and can be done using the Flask development server
using the following commands:

```bash
export FLASK_APP=app/app.py
export FLASK_DEBUG=True
flask run
```

### Utility Scripts

#### Seeding the test Configuration Database Service

In order to provide a set of test data in the test Configuration Database 
service a utility script is provided in the `utils` folder called `init_db.py`.

This will drop all existing data in the Configuration Database and replace 
it with a set of randomly created Scheduling Block Instance data structures.

This can be run with the command:

```bash
python3 -m utils.init_db
```


