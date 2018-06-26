# SIP Processing Controller Scheduler

## Introduction

This component implements a prototype of the SDP Processing Controller
Scheduler service. This serice uses instructions from TM, provided
via the Processing Controller Interface service(s), to schedule tasks in the
form of Processing Blocks (PBs) for execution on the SDP system.

This service is backed by the Execution Control Configuration Database
service which provides a data resource (the source of truth) and event queue
for reasoning about all Processing Blocks known to SDP. In SIP this is
currently implemted using Redis via a Configuration Database client API.

As described in the SDP architecture documentation, SDP expects to schedule
processing tasks using a two level scheduling model. In this model,
the high level (coarse grain) scheduling Processing Blocks is largely
determined a priori by TM using a model of SDP resources and estimated
resource costs of each task. It is this level of scheduling that is performed
by this service.

Below this level, the scheduling of the workflow which define the
staging, processing, and cleanup operations needed to execute each Processing
Block is handled by instances of the Processing Block Controller service.

The scheduling of Processing Blocks, performed by this Service therefore
requires the following functions:

- Registration of Processing Blocks with the scheduler
- Removal of Processing Blocks from the scheduler (including aborting
  processing if required).
- Retrieval of information on Processing Blocks.
- Evaluation of resource availability for running Processing Blocks
- Provisioning of available resources for running Processing Blocks
- Initialising the execution of a Processing Block (which also involves
  a Processing Block Controller Service)
