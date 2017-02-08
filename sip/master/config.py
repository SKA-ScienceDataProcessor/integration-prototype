"""Global configuration.

This file defines the master control global data.
"""

state_machine = None
heartbeat_listener = None
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

This dictionary records the state and other dynamic information about the
slaves. It includes:
- the slave type; an index into the slave map.
- the slave's state as reported by (or the absence of) heatbeat messages
- the state the slave ought to be in
- the previous state of the slave
- timeout counter: The number of missed heartbeats left to go. 

The polling loop decrements the timout counter each time it runs and if 
it goes to zero the slave is declared to be timed-out. Each time a  
heartbeat message is received the counter is reset to the value of  
'timeout' from the config dictionary. 
""" 
