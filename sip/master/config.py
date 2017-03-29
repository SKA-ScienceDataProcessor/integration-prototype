"""Global configuration.

This file defines the master control global data.
"""

state_machine = None
logserver = None

resource = None
"""Resource manager."""

slave_config = {}
"""Slave map.

This dictionary defines the properties of all the slave controllers that 
we might want to start. It is indexed by the slave 'name' (just some 
arbitrary string) and each entry is a dictionary containing at least the 
following 
 
- The 'launch policy' of the slave. This allows the master control to use the 
  appropriate method to start the slave 
- 'timeout': The number of polling intervals we are prepared to not 
   see a heartbeat message for before declaring the slave awol. 
  
Other stuff in the entry contains the info need to start the slave.
""" 

slave_status = {}
"""Slave status.

This dictionary the state and other information about the slaves that is
only known at run time.. 

It includes:
- "type": the slave type; an index into the slave map.
- "task_controller": The SlaveTaskController object that can send commands
to the slave
- "state": The state machine that shadows the state of the slave controller
- "descriptor": The PAAS descriptor for the slave controller service.
""" 
