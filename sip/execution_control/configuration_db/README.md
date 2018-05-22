# SIP Configuration Database Service

The Configuration Database is a backing service for use by other Execution
Control components.

## Roles and Responsibilities

- Stores configuration information for use by Execution Control components.
- In the current version of SIP the configuration database service 
  stores data and metadata as associated the Master Controller functions as 
  well as the Scheduling Block Instances Known to SDP.
- It is expected that the Configuration Service will be used in some capacity 
  by most, if not all of the Execution Control Components.
- The configuration Database provided by this service will be accessible 
  through an API in the configuration database client library. This provides 
  client services with an abstraction to the database for reasoning about 
  information stored without requiring detailed knowledge of the way data is 
  stored. This choice gives us the option to explore other database 
  technologies at a later date without extensive refactoring of services
  which depend on the database.
