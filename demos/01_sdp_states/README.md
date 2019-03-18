# SIP Demo: Monitoring and Control of the state of SDP

## 1  Introduction

This demo gives a brief introduction to the following:

1. How the set of persistent SDP services in SIP are started using Docker Swarm.
2. The interface provided by SIP SDP prototype for monitoring and control of
   the high-level SDP state.

While a brief introduction is given here in the following sections, for a
more detailed discussion on both these topics please also refer to
Section 7.4 of the
[SIP prototyping report](https://drive.google.com/open?id=1K9dQQ0yiEFwcgc0e3a5EP1jXzRrgj8Lk).

### 1.1  Starting SDP Services

In SIP, the set of persistent services that implement the core components
of SDP system are started and managed by
[Docker Swarm](https://docs.docker.com/engine/swarm/).
We adopted this this approach as it allowed us to prototype the SDP system
as a set of loosely coupled (micro-)services, allowing agility
and resilience in both development and deployment.

While we note that Docker Swarm is unlikely to chosen in the solution
architecture for the production SDP system (as since making this choice
other solutions such Kubernetes have evolved to provide a much richer set of
features and have a far larger community support), for SIP
Docker Swarm proved very effective due to its relatively simplicity
and low barrier to entry. For these reasons, Docker Swarm still provides an
excellent proof-of-concept environment for testing
[Container Orchestration](https://devopedia.org/container-orchestration)
in an an SDP context, which was a key aim of the SIP prototyping effort.

In order to deploy the prototype SDP services, Docker Swarm uses
[Docker Compose](https://docs.docker.com/compose/) file format. This is used
to specify the desired state of the system as a set of configured
[Docker Services](https://docs.docker.com/engine/swarm/how-swarm-mode-works/services/).
For the set SDP services prototyped in SIP this is demonstrated in Section 3.1.


### 1.1.2  Monitor and Control of SDP

Monitoring and control of SDP is a core function provided to telescope
operators using a [Tango Control](http://www.tango-controls.org/) interface.
For SDP this interface provides two main functions:

1. Reporting and manipulating the state of SDP
2. Scheduling Processing on the SDP system

In this demo we focus on the first of these functions.
For an introduction to scheduling processing in SDP as prototyped in SIP,
please refer to the demo folder `02_running_a_workflow`.

The primary components involved monitoring and controlling the high-level
state of SDP in the SIP prototyping are shown in the cartoon below:

![Components Cartoon](figures/components_cartoon.png)

Here the external interface for monitoring and control is provided by the
**Tango SDP Master device**. This is supported a backing service, called
the **Execution Control Master Controller** which handles most
of the functionality needed to maintain and control the state of SDP.
This provides separation between the interface service and the service
monitoring and manging the state of SDP. Communication and consistency
between the Tango Master Device and Execution Control Master Controller is
orchestrated via a data model (shown in the Figure below), which is stored
in the **Execution Control Configuration database**. This simple data model
describes the high-level SDP status and the status of individual SDP services
in terms of a **current state** and a commanded or **target state**. We note
that while implementation does not consist of a true state machine, this
eventually consistent representation of the SDP state is a far more practical
solution to representing the state of a system which is composed of a set
loosely coupled services, and where resilience and recovery from failure are
key quality attributes.

![States Logical Data Model](figures/states_data_model.png "")

The diagram below describes the logical state machine for each of the
individual services in the SIP prototype.

![Service States](figures/service_states.png "")

This diagram, defines the states and state transitions for SDP services
services as implemented in the current version of SIP. In this model
there are five states.

- `INIT` when starting up
- `ON` when the service is running normally
- `OFF` when the service is off
- `ALARM` when the service has encountered a recoverable error
- `FAULT` when the service has encountered an unrecoverable error

The overall, high-level, state of SDP is then a function of the state of
individual services. While in SIP we have not prototyped this mapping,
we have implemented a set of allowed state transitions for the high-level
state of SDP as shown in the diagram below.

![SDP State](figures/sdp_states.png "")

In this diagram (above), the SDP state can transition between five main states:

- `INIT` when services are initialising
- `STANDBY` when all services have read `ON` or if the SDP is commanded to abort all processing and not accept new Scheduling Block Instances (SBIs)
- `DISABLE` when SDP is commanded to stop scheduling and accepting new SBIs
- `ON` when SDP is fully operational and will accept new SBIs
- `OFF` when the SDP is off or commanded to turn off

Each of the states also can enter two different substates when errors occur,
these are:

- `ALARM` when SDP encounters a recoverable error
- `FAULT` when SDP encounters a unrecoverable error

## 2  Getting started

In order to run this demo you will need a Docker installation (eg.
<https://www.docker.com/products/docker-desktop>) and access to a terminal
prompt where the Docker CLI is installed. Docker must also be configured in
Docker Swarm mode, as described in Section 2.1 below.

While all Docker commands needed to run this demo are described below,
for additional information on how to use Docker, please refer to the
documentation pages at <https://docs.docker.com/>.

### 2.1  Setting up Docker Swarm

Docker must be configured to operate as a Swarm cluster.
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

## 3  Running the Demo

### 3.1  Starting the SIP SDP operational system services

As described in Section 1.1, all persistent services in SIP are deployed using
Docker Swarm as a Docker
[stack](https://docs.docker.com/engine/swarm/stack-deploy/).
This makes use of a Docker Compose file (`docker-compose.yml`) which describes
the set of services that should be started along with their configuration.
Configuration information provided to Docker Swarm includes specific Docker
image versions for each service, network port configuration, and
environment variables which are passed to the container applications that
make up the service.

To start all SIP SDP services, from a terminal with a prompt in the
`demos/01_sdp_states` folder, run the following command:

```bash
docker stack deploy -c docker-compose.yml sip
```

The last argument in this command, `sip`, is the name of the stack
and for this demo consists of a set of 17 services. One can verify the
status of the `sip` services started by issuing the following command:

```bash
docker stack services sip
```

An example of the output of this command is shown below:

![SIP Services](figures/services.png "")

If the output of this command reports that services reached not yet reached
a replication level of `1/1`, as indicated by the `REPLICAS` column, please
wait until this is the case before proceeding. As for this demo Docker Images
will be downloaded from the public
[SIP Docker registry](https://cloud.docker.com/u/skasip) this can take several
minutes so please be patient. We note that a a production system can avoid
much of this start-up delay by employing a local cache or registry of
pre-approved Docker images.

If we inspect the list of Docker services (see Figure below) we can see by the
service names that there are three types of services that have been started.
As shown in the Figure below, these are light-weight prototypes of a number
of the Execution Control, Tango Control and Platform services identified in
the SDP architecture.

![Services & Components](figures/services-components.png)

### 3.2  Monitoring and Control of SDP

With a set of SDP Services started, (see Section 3.1), we can now use the
Tango Control interface to query and command the state of SDP.

This is done by first obtaining an interactive Tango client interface
capable of communicating with the SDP Tango Control devices we have started.

A special Docker container has been provided for this purpose which starts an
[iTango](https://pypi.org/project/itango/) prompt connected to the Tango
services we have started in section 3.1

A script has been provided to launch this interface:

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

The `DeviceProxy` function provides the client with an easy to use interface
to a device, here the SDP Tango Master device named `sip_sdp/elt/master`.

In addition to reporting and commanding the SDP state, the SDP Master Device
is able to report a number of additional attributes such as its version, its
health status, the list of SDP Services it is tracking, and the status of
the Tango device. These can be obtained with the following commands:

```python
md.version
md.health
md.sdp_services
md.status()
```

Before interacting with the SDP state further, please obtain a second
terminal which follows the Execution Master Controller. We do this so that we
can monitor what the Execution Control Master Controller is doing in
response to Tango Master Device interactions. To do this, start a new
terminal and use the following script (provided in this folder) to start
watching logs from the Execution Control Master Controller logs.

```bash
./follow_master_controller_logs.sh
```

Going back to the original `iTango` terminal prompt, we can now start
interacting with the Tango master and see the response in the logs of the
Execution Control Master Controller backing service.

Once the SDP has started up and all services are online, it will be in the
'standby' state. From the iTango prompt, we can verify this by querying the
current state of SDP as follows:

```python
md.current_sdp_state
```

From standby we can either transition to 'ON' or 'OFF'. The set of allowed
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

We could have also set SDP to `OFF` but that is currently an end state
which reburies manual intervention (essentially a SDP restart) to recover from.

Upon setting the target sdp state to `ON`, the Execution Control Master
Controller, which is watching for target state change events via the
Execution Control Configuration database, will respond to the state change
request and perform any actions needed to bring the state of SDP to the `ON`
state. Please check that this can be seen in the in the Execution Control
Master Controller logs that we are following in a 2nd terminal.

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

In addition to getting the high-level state of SDP, the
`get_current_service_state()` command on the Tango Master allows us to query
for the state of individual SDP services. For example, to obtain the state of
Execution Control Master Controller we issue the following command:

```python
md.get_current_service_state('MasterController')
```

At this point, the prototype does not allow the Tango interface to set
the value service states individually.

### 3.3  Cleaning up

Exit the `iTango` prompt by typing `exit` in the prompt. This will exit
and remove the container that was started to provide this prompt.

To stop following the Master Controller logs, issue a `ctrl-c` (`SIGINT`)
in the terminal which the logs are being displayed.

To clean up from running the demo, to remove all services started use the
following command:

```bash
docker stack rm sip
```

Also one should remove the Docker volume created to persist the Tango MySQL
database for this demo:

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
