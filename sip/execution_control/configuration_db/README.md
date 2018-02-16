# SIP Configuration Database Service

## Roles and Responsibilities

- Stores configuration information for use by Execution Control components.
- In the current version of SIP (Sprint 2018A) the configuration service 
  will primarily store data concerning as associated with Scheduling Blocks
  and Processing Blocks, and Internal SDP states.  
- Scheduling blocks can be described as a root aggregate consisting of 
  Processing Block objects which are further decomposed into workflow stage 
  objects.
- It is expected that the Configuration Service will be used in some capacity 
  by most, if not all of the Execution Control Components.
- Information stored in this service will be accessible through a client 
  library which provides an abstracted Python API for reasoning about 
  information stored in the database in a way that does not require detailed
  knowledge of the internal storage representation. This choice gives us the
  major advantage of client services not needing to know details of the 
  underlying database technology so they can reason about the data
  model rather than representation of the data within the database, as well as
  the option to explore other database technologies at a later date if needed 
  without needing extensive refactoring of other services.
  
Additional roles that ***might*** be assigned to the Configuration Service and 
are under consideration:

- Service discovery. Although we are currently going to be using a combination
of built-in features of Docker and Tango for this, we recognise that we may 
need to replace or extend Service Discovery using the Configuration Database 
Service at a later date. 
- Celery message broker for Processing Block Controller workers.
- Celery results backend Service for Processing Controller workers. 
