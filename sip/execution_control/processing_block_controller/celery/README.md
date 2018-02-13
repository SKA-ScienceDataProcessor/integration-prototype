# SIP Processing Block Controller

## Description

Replicated, containerised service providing a set of Celery workers backed by 
a broker which could either by a (/the?) configuration database 
(current default) or a message queue run as a separate service.
- Workers are started by the Processing Controller (Scheduler)
- Workers interact with the Configuration Service to provide asynchronous 
  updates on the state and progress of the Processing Block they are running
- Workers interact with interfaces provided by Platform Services and SDP 
  Services Components to execute the various workflow stages defined for the 
  Processing Block.
- The number of celery workers can be scaled by controlling the replication of 
  the Processing Block Controller service container instances. This scaling 
  could be done automatically based on worker load or contention or by the 
  Processing Controller Scheduler based on the number of active Processing 
  Blocks or some other suitable metric or heuristic.

## Provided Interfaces

- None, unless we need / choose to connect a results backend.

## Required Interfaces

- SDP Configuration Database Service
- Celery Broker (could be the Configuration Service)
- Various Platform services Interfaces
- Various SDP Services Interfaces

## Component View

![](https://drive.google.com/uc?id=1QPJgRPpF6_X4G0Pk6Ig9cpHPN_GrFj2Q)

- *Note the Broker, Backend, and Configuration Service could all be using the
   same database in deployment if that was desired*
