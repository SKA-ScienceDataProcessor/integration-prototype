# SIP Configuration Service (Redis variant)

Placeholder for the Redis based Configuration Service.

This folder will contain the client code, standalone deployment script 
(eg docker-compose.yml) and any unit tests and examples used to demonstrate 
or verify this service.

Scripts for a larger SIP deployment making use of this service are found in 
the top level `deploy` folder. 

## Quickstart

To set initial data to the configuration database
python3 -m utils.set_initial_data

To test master controller run the unittest
python3 -m tests.test_master_client

Note - For now, after the unittest is executed, flush out the database and re-run the initial data script
       otherwise the unittest will fail

TODO:
Fix the teardown function in the master controller unit test
Sort how the connection needs to work in the client
Start implementing the controller_client.py

