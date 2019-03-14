# SIP Demo: Monitoring and Control of the state of SDP

## 1.  Introduction

This demo provides a brief introduction to:

1. How the set of persistent SDP services in SIP are started and managed by
   Docker Swarm.
2. The interface provided by SIP SDP prototype for monitoring and control of
   the high-level SDP state.

For a more detailed discussion please also refer to Section 7.4 of
the [SIP prototyping report](https://drive.google.com/open?id=1K9dQQ0yiEFwcgc0e3a5EP1jXzRrgj8Lk).

### 1.1.  Concepts

#### 1.1.1  Starting SDP Services

The increasing widespread adoption of
[Container Orchestration](https://devopedia.org/container-orchestration)
tools for deploying applications in a resilient and ... way
[cloud-native](https://www.cncf.io/) methodology to code development is a
huge advantage to SDP.

As such, in SIP we have chosen to deploy all persistent services using
[Docker Swarm](https://docs.docker.com/engine/swarm/), to deploy and
manage all prototype SDP services. Swarm uses
[Docker Compose](https://docs.docker.com/compose/) to specify a desired
state of the system in terms of Docker Services. In Section xxx we start all
SDP services using this.

### 1.1.2  Monitor and Control of SDP

Monitoring and control of SDP is a function provided to telescope operators
over a Tango Control interface. For SDP this consists of two main areas:

1. Reporting and manipulating the state of SDP
2. Scheduling Processing

In this demo we focus on the first of these two areas. Demo `02_running_a_workflow` then introduces the second of these areas.

In SIP, the interface for control and monitoring of SDP follows a two stage model in which a high-level state of SDP is based on the state of the set of key persistent services which provide the core functions of the system.

The data model for SDP States..

![States Logical Data Model](figures/states_data_model.png "")


In SIP, as in SDP architecture, the state of SDP is reported and set by the SDP Tango Master device. We note that this is not implemented as a true state machine but reports an eventually consistent version of the system state as evaluated and managed by the Execution Control Master Controller service. This approach decouples the commanded (target) state of the system from the current state and allows the system to be much more reliant to failure / failover of individual services. In this model, unless
significant parts of the system is down it is likely that some
functionality can be maintained and recovery from failure is relatively straightforward (ie by restarting or rolling back services)

Individual Services in the SIP prototype can between the following states, described by the diagram below.

- `INIT` when starting up
- `ON` when the service is running normally
- `OFF` when the service is off
- `ALARM` when the service has encountered a recoverable error
- `FAULT` when the service has encountered an unrecoverable error

![Service States](figures/service_states.png "")

The overall state of SDP is a function of the state of individual
services and can be in one of the following states with transitions
defined by the diagram below.

- `INIT` when services are initialising
- `STANDBY` when all services have read `ON` or if the SDP is commanded to abort all processing and not accept new Scheduling Block Instances (SBIs)
- `DISABLE` when SDP is commanded to stop scheduling and accepting new SBIs
- `ON` when SDP is fully operational and will accept new SBIs
- `OFF` when the SDP is off or commanded to turn off

Each of the states also can enter two different substates when
errors occur, these are:

- `ALARM` when SDP encounters a recoverable error
- `FAULT` when SDP encounters a unrecoverable error

![SDP State](figures/sdp_states.png "")

## 2.  Getting started

To run this demo you will need a Docker installation (eg.
<https://www.docker.com/products/docker-desktop>) and access to a terminal
prompt where the Docker CLI is installed. Docker must also be configured in
Docker Swarm mode, as described in Section 2.1 below.

While all Docker commands needed to run this demo are described below,
for additional information on how to use Docker, please refer to the
documentation pages at <https://docs.docker.com/>.

### 2.1  Setting up Docker Swarm

For this demo, Docker must be configured to operate as a Swarm cluster.
The following command can be used to determine if this has been already
configured:

```bash
docker info | grep Swarm
```

This will report that the Swarm is `active` or `inactive` depending if
Docker is configured in Docker Swarm mode. If the Swarm cluster is
`inactive` (not started), it should be started with the following command:

```bash
docker swarm init
```

## 3.  Running the Demo

### 3.1.  Starting the SIP SDP operational system services

As described in Section 1.1.1, all persistent services are deployed as a
Docker Swarm [stack](https://docs.docker.com/engine/swarm/stack-deploy/)
which makes use of the Docker Compose file `docker-compose.yml` found in this
demo folder. This file describes which services should be started along with
configuration information provided to Docker Swarm specifying various runtime
options such network port configuration and environment variables provided
to the container applications.

To start the SIP services, from a terminal with a prompt in the
`demos/01_sdp_states` folder, run the following command:

```bash
docker stack deploy -c docker-compose.yml sip
```

The last argument in this command, `sip`, is the name of the deployment stack
and consists of a set of 17 services defined in the Docker Compose file.

Once started, you can verify the `sip` services running with the following
command:

```bash
docker stack services sip
```

An example of the output of this command is shown below:

![SIP Services](figures/services.png "")

If the output of this command reports that not all all services reached a
replication level of `1/1`, as indicated by the `REPLICAS` column, please wait
until this is the case before proceeding.

In order to run this demo it is likely the Docker Images used will have to be
downloaded from the [SIP Docker registry](https://cloud.docker.com/u/skasip)
which can take several minutes.

If we inspect this list in more detail (see Figure below) we can see a
that there are three types of services that have been started in this demo,
distinguished by a name prefix of `sip_ec_`, `sip_platform_`, or `sip_tc_`.
As shown in the Figure below, these are light-weight prototypes of a number
of the Execution Control, Tango Control and Platform services identified in
the SDP architecture.

![Services & Components](figures/services-components.png)


### 3.2.  Monitoring and Control of SDP

With a set of SDP Services started, (see Section 3.1), we can now use the
Tango Control interface to query and command the state of SDP.

This is done by first obtaining a Tango client interface capable of
communicating with the SDP Tango Control devices we have started. A special
Docker container has been provided for this purpose which starts an
[iTango](https://pypi.org/project/itango/) prompt connected to the Tango
services we have started.

A script, run with the following command, has been provided to launch this
interface.

```bash
./itango_prompt.sh
```

Once this has started we can list the SDP Tango devices with the
following command:

```python
lsdev
```

An example of the output of this is shown in the figure below.

| ![List SIP Tango devices](figures/itango_01.png) |
|:--:|
| Excerpt from list of Tango Devices returned from the `lsdev` command |

In the SIP prototype, the high-level state of SDP is reported using the
Tango Master device. We can now make a connection to this device using the
following command:

```python
md = DeviceProxy('sip_sdp/elt/master')
```

The `DeviceProxy` function provides the client with an easy-to-use interface
to the named device, which here is the SDP Tango Master prototype.

In addition to reporting and commanding the SDP state, the SDP Master Device
is able to report a number of additional attributes such as its version, its
health, the list of SDP Services it is tracking, and the status of the device.
These can be obtained with the following commands:

```python
md.version
md.health
md.sdp_services
md.status()
```

Before interacting with the SDP state, obtain a second terminal which follows
the Execution Master Controller logs so that we can monitor what the EC master
is doing in response to Tango Master Device actions.

Start a new terminal and use the following command to start watching logs
from the Execution Control Master Controller.

```bash
./follow_master_controller_logs.sh
```

Using the `iTango` SDP Tango Master client terminal start interacting with the
state of SDP.

When the SDP starts it starts in the 'standby' state. We can verify this
by querying the current state of SDP as follows:

```python
md.current_sdp_state
```

From standby we can either transition to 'on' or 'off'. The set of allowed
target or commanded states provided by the Master Device can be queried
with the following `allowed_target_sdp_states` attribute as follows:

```python
md.allowed_target_sdp_states
```

We can now set the state of the SDP to `ON` by setting the value of the
`target_sdp_state` attribute:

```python
md.target_sdp_state = 'on'
```

Upon setting the target sdp state to `ON`, the Execution Control Master
Controller, which is watching for target state change events via the
Execution Control Configuration database will respond to the state change
request and perform any actions needed to bring the state of SDP to the `ON`
state. This should be reflected in the Master Controller logs.

After a short time, if we now check the current state of SDP with the Tango
Master device using the following command:

```python
md.current_sdp_state
```

It should now correctly report the SDP is `ON`.

As reported by:

```python
md.allowed_target_sdp_states
```

from the `ON` state we can transition to either `OFF`, `STANDBY`, or `DISABLE`.

Transitioning to any of these states can be done setting the `target_sdp_state`
attribute in the same way as we did with `ON`.

In addition to getting the current state of SDP, the
`get_current_service_state()` command on the Tango Master allows us to query
for the state of individual SDP services. For example, to obtain the state of
Execution Control Master Controller we issue the following command:

```python
md.get_current_service_state('MasterController')
```

### 3.3.  Cleaning up

To remove all services started in this demo use the following command:

```bash
docker stack rm sip
```

To remove the Docker volume created to persist the Tango MySQL database:

```bash
docker volume rm sip_tango_mysql
```

*Note: you may have to wait a few seconds for the services to be removed
before Docker allows the volume to be removed*

Finally, occasionally a number of terminated containers can be left over from
when tearing down the stack. You can check this by issuing the command:

```bash
docker ps -a -f status=exited -f name=sip_
```

If this returns any containers, these can be removed with:

```bash
docker rm -v -f $(docker ps -a -q -f status=exited -f name=sip_)
```

