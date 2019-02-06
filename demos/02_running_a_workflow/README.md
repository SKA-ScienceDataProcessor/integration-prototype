# SIP Demo: Running a workflow

## 1.  Introduction

This demo gives a brief introduction to how a workflow can be executed
using the SIP prototype. To demonstrate this a simple containerised
'mock' workflow is run. While this workflow does not perform any
actual processing function, it has been designed to capture the essential
elements of how a workflow might be run on the SDP system.

### 1.1.  Concepts

The figure below shows the key components of the SIP prototype of the SDP
system involved in executing a workflow.

![Workflow components](https://docs.google.com/uc?id=1ri_wR0aIXuxfGra3Sjzq-wqpPhItUEgw "")

Workflows are scheduled for execution by issuing a request to the SDP Tango
interface in the form of a command that accepts a **Scheduling Block Instance
(SBI) configuration** object. A SBI object is a high-level data structure
used for scheduling across all elements of the SKA, which includes the SDP.
For the purposes of SDP, SBIs contain a number of Processing Block (PB)
objects, which define a workflow that should be executed to a task such as
ingest data or processing data stored in the SDP buffer.

For the purposes of this demo the interface for scheduling SBIs is
is provided by the **Tango SDP Master** device. While in a full
SDP deployment the SDP Subarray node devices as also expected to play a role
in this, to keep things simple, these are not included in this demo.

In order for PBs (contained the SBI) to be accepted by SDP, the workflow
specified by the PB must be already registered with the system.
This ensures that only workflows that have been validated and tested are
allowed to run. In SIP, workflows are registered by adding them
to the **Execution Control (EC) Configuration database** using
a SIP **Workflow Definition** format. This is a set of JSON or YAML
files which define the stages (or steps) required to execute a workflow,
along any parameters that can be provided to modify its runtime behaviour.

By issuing the SBI request, PB data objects defined in the SBI are created
in the EC Configuration Database. PB objects in the database store a
complete meta-data description of the PB, its workflow and hold a reference
to a log of events describing all actions taken to the PB object.

PB events are monitored by a number of services including the
**Processing Controller**, the component responsible for scheduling
PB workflows for execution. Once the Processing Controller detects an event
notifying it of a new PB data object, it adds the PB to a priority queue of
PBs being considered for execution. The Processing Controller continuously
monitors PBs in this queue to determine which PBs can be executed. For PBs
determined ready to be executed, the Processing Controller then starts a
**Processing Block Controller** which is responsible for executing them.

In SIP, a PB workflow is run as a set of **workflow stage containers**,
deployed using the Docker Swarm **Container Orchestration** according to the
specification in the workflow definition. As each workflow stage executes, the
Processing Block Controller updates the PB data model and issues events to
notify other services of the progress of the workflow execution.

Upon completion of the workflow, the Processing Block Controller is destroyed
and resources assigned to the workflow are released for assignment to other
PBs.

## 2.  Getting started

To run this demo you will need a Docker installation (eg.
<https://www.docker.com/products/docker-desktop>) and access to a terminal
with the Docker CLI installed. Docker must also be configured in Docker Swarm
mode, as described in Section 2.1 below.

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

The services needed to deploy the SIP prototype components for running a
workflow can be started as a
[Docker Swarm stack](https://docs.docker.com/engine/swarm/stack-deploy/)
using the Docker Compose file `docker-compose.yml` found in this folder.

From a terminal with a prompt in the the `demos/02_running_a_workflow` folder,
run the following command:

```bash
docker stack deploy -c docker-compose.yml sip
```

where `sip` is the name of the deployment stack and consists of a set of
eight services defined in the Docker Compose file.

Once started you can verify that the `sip` services running with the
following command:

```bash
docker stack services sip
```

An example of the output of this command is shown below:

![SIP Services](https://docs.google.com/uc?id=12x_MZKJHv5513VC-o91KsvjLc2FT6zlQ "")

If all services have not yet reached a replication level of `1/1`
(as shown by the `REPLICAS` column), please wait until this is the case
before proceeding to the next step. When running the demo for the first time,
as part of starting the stack, Docker images will be downloaded from the
[SIP Docker registry](https://cloud.docker.com/u/skasip) which often takes a
few minutes, so please be patient!

### 3.2.  Defining and registering a workflow definition

As described in Section 1.1, in order to run a workflow, it must first be
registered with the SIP Execution Control Configuration Database.

In this demo, we will run a simple mock workflow consisting of three
linear stages (set-up, processing, and clean-up). A workflow definition for
this is provided in the `workflow` sub-folder. This folder contains the
top-level workflow definition file `mock_workflow_1.0.0.json` along with a
directory structure called `templates` which defines what is executed for
each workflow stage. In this workflow definition, JSON command line argument
use [Jinja2](http://jinja.pocoo.org/docs/2.10/) templates to define a duration
parameter which modifies the duration each state is run for.

In order to register this workflow with the SIP Execution Control system
we first need to start a terminal with the SIP CLI tools installed.

To do this run the script:

```bash
./demo_prompt.sh
```

This starts a configured interactive Docker container which creates
a bash prompt with the dependencies installed to interact with the SIP
services started in §3.1. This demo prompt will take the form:

```bash
sip@<container id>:~$
```

where `<container id>` is the short 12 letter hash identifying the container
that has been started.

*Note: You can exit this container by typing `exit` on the prompt, but in
doing so, all bash command history and any files created inside the container
will be lost. This is because the the container is destroyed when the
interactive session is terminated.*

In this prompt issue the following command to register the workflow with the
EC Configuration database:

```bash
skasip_config_db_register_workflows workflow
```

If successful, you should see the message:

```bash
* Loading workflow template: workflow/mock_workflow_1.0.0.json
```

### 3.3.  Scheduling a workflow for execution

In order to execute a workflow, it must be scheduled to run on the system
using a Tango Control interface device. For the purposes of
this demo, this is achieved by issuing a `configure` command on the
Tango Master device. The `configure` command takes a JSON
string that specifies a Scheduling Block Instance (SBI) configuration object.
Section 1.1 describes this process in more detail.

As (in §3.2) we have already registered a workflow with the SIP prototype
system, this can now be scheduled for execution by issuing a SBI configure
command.

When starting the SDP services in §3.1, this included a containerised
Tango SDP Master device which we will now issue a SBI configure command to.

In order to interact with this tango device, in the bash prompt started
in §3.2 using the `./demo_prompt.sh` script, enter the following command:

```bash
itango3
```

This will start an interactive [iPython](https://ipython.org/) session with the
[iTango](https://pythonhosted.org/itango/) extension installed. This 'iTango'
session provides a simple and quick way to connect to the SIP Tango Master
device started in §3.1

To create a connection to the SIP Tango Master enter the command:

```python
md = DeviceProxy('sip_sdp/elt/master')
```

This returns a [DeviceProxy](https://pytango.readthedocs.io/en/stable/client_api/device_proxy.html)
object, with the name `md` which can be used to communicate with the SDP
Tango Master.

We can test this connection using the following commands to query for
the list of SBIs or PBs known to the SDP:

```python
md.scheduling_block_instances
md.processing_blocks
```

As we have not yet scheduled any PBs however, both of these commands should
return:

```python
'{"active": [], "completed": [], "aborted": []}'
```

Before being able to issue an SBI configuration request, system must be in
the must be in the 'on' state. This can be achieved by setting the
`target_sdp_state` attribute on the Tango Master to 'on' with the following
command:

```python
md.target_sdp_state = 'on'
```

(For a more complete demonstration of monitoring and setting the state of the
SDP, see `demo_01_sdp_states`).

Before proceeding, please verify that the SDP has reached the 'on' state by
querying the value of the `current_sdp_state` attribute as follows:

```python
md.current_sdp_state
```

This must report the SDP as being 'on' before continuing with this demo.

We can now issue a `configure` command to the Tango Master device to
schedule a Processing Block with workflow we have registered with the system
in §3.1.

As described in Section 1.1, the configure command takes a JSON SBI
configuration object. As the creating an SBI JSON string takes some time,
a utility script, called `generate_sbi_config.py` which generates a suitable
SBI JSON string has been provided for this demo.

To use this script to generate an SBI configuration, run the following command
from the `iTango` prompt:

```python
%run generate_sbi_config.py 1
```

This will generate a SBI configuration dictionary and the equivalent
JSON string in the workspace as the variables `sbi_config` and `sbi_json`
respectively.

If successful the script should report:

```bash
* Generating SBI: SBI-20190211-sip-demo-001, PB: PB-20190211-sip-demo-001
```

and the command:

```python
print(json.dumps(sbi_config, indent=2))
```

will print a formatted of the SBI configuration string.

We now have everything in place to be able to schedule the test workflow to
run on the SIP SDP prototype. Before doing so however it is useful to set up
some terminals so that we can monitor what happens.

To do this start three **additional** terminals that:

1. Follow logging output from the Processing Controller
2. Follow logging output from the Processing Block Controller
3. Watch for Docker containers used to execute the workflow

Scripts found in the root of the `demo_02_running_a_workflow` folder are
provided to do this.

1. `follow_pc_logs.sh` should be run to follow the Processing Controller logs
2. `follow_pbc_logs.sh` should be run to follow the Processing Block Controller
   logs
3. `watch_workflow_stages.sh` should be run to watch for Docker containers
   involved in executing the test workflow.

Once these are started, you should have four terminals open, three for
monitoring what happens when the SBI is scheduled, and one with the previously
started iTango that we will need to issue the SBI configuration request.
This should look a bit like the screen shot below:

![Workflow Monitoring](https://docs.google.com/uc?id=1Io2KAzF0_HiVgJlOJ6gbsgLQfbZsSo4X "")

We can now issue a SBI configuration request to the SDP Master device and
watch what happens. To do this, run the command:

```python
md.configure(sbi_json)
```

This command will register the PB defined in the SBI with the EC Configuration
database and generate an event notifying the SDP PB scheduler, the Processing
Controller of this.

The Processing Controller, which is monitoring for new PBs, will detect the PB
and add it to a queue of PBs being considered for execution. This can be
seen in the terminal that is following the Processing Controller log output.
An example of this can be seen in the screenshot below:

![Processing Controller](https://docs.google.com/uc?id=12AyxLu4PCDnNeLh0fIC31jawd5VFQHQz "")

Once a PB is deemed ready for execution, a Processing Block Controller is
started to execute the workflow defined in the PB. In SIP, the Processing
Block Controller is implemented as a Celery task, which is a process spawned
in a Celery worker container specialised for executing Processing Blocks.

The terminal configured to view logs of the Processing Block controller
(screenshot below) shows what happens when the Processing Block Controller
task starts running and executes the workflow.

![Processing Controller](https://docs.google.com/uc?id=1AMpu-pqXgGaOqvn6OsPm5Pu8NITnBcPA "")

The test workflow used in this demo is executed as a series of three stages,
each run as Docker containers using Docker Swarm in the order defined by the
workflow definition. In this demo, these containers simply wait for a
configured number of seconds before exiting, but could easily be replaced
by containers that actual SDP functions. In SIP have developed a number of
such workflow containers but as these are far more complicated to configure
and take longer to run they were deemed not suitable for this demo.

Once the workflow has started executing, the terminal set up to monitor
for these containers will show them being created and removed as each workflow
stage starts and ends (an example of which is shown in the screenshot below).

![Processing Controller](https://docs.google.com/uc?id=1lFF99zKpaiYq6FRz5gA5En8pkqwwLz0F "")

Once this has completed if one wants to repeat this test, a new SBI must be
generated. This is because each SBI and PB has is required to have unique
identifier in the system and if this is not the case the SBI will be rejected.

The SBI generation script (used above) allows for this. The script has a takes
an integer argument that can be used to generate a new SBI and PB id. In the
step above we generated a SBI with a suffix `001`, as the argument
to the generator was `1`. We can therefore use this to generate a new SBI
with an id with a suffix `002` with the the following command:

```python
%run generate_sbi_config.py 2
```

It is then possible to configure this new SBI configuration with the
SDP Master, as before, and watch it execute in the system.

Once PBs have been executed on the system, it is possible to query their
progress using the command:

```python
md.processing_blocks
```

Having run one or more PB workflows, this command should report a number
of PBs as having been completed.

### 3.5.  Cleaning up

In order to clean up this demo, first exit the `iTango` prompt and demo prompt
container by issuing `exit` command (twice). Once back at the terminal prompt
on the host where we started, one can terminate all Docker services and storage
volumes using the following commands:

```bash
docker stack rm sip
docker volume rm sip_config_database sip_tango_mysql
```

Occasionally Docker will leave behind exited containers. If this is the case,
they can be cleaned up with the following command:

```bash
docker rm -v -f $(docker ps -a -q -f status=exited)
```

For a full clean up, you may also want to remove all of the `skasip/*`
Docker images on your system. (WARNING: this will remove all `skasip/*` not
just those downloaded for this demo!). If so, this can be done with the
following command:

```bash
docker image rm --force $(docker image ls --filter=reference='skasip/*' -q)
```
