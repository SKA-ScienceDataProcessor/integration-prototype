""" Global configuration

This file defines the master control global data.
"""

state_machine = None
heartbeat_listener = None

slave_config = {}
""" Slave map 
This dictionary defines the properties of all the slave controllers that 
we might want to start. It is indexed by the slave 'name' (just some 
arbitrary string) and each entry is a dictionary containing at least the 
following 
 
- The 'type' of the slave. This allows the master control to use the 
  appropriate method to start the slave 
- 'timeout': The number of polling intervals we are prepared to not 
   see a heartbeat message for before declaring the slave awol. 
  
Other stuff in the entry contains the info need to start the slave (e.g. 
what host it should run on). 
""" 

slave_status = {}
""" Slave status

This dictionary records the state and other dynamic information about the
slaves. It includes:
- the slave's state, which can be one:	 
 - an empty string: Either we have never tried to start the slave or we have shut it down cleanly. 
 - 'running': we managed to start the slave and we are receiving heartbeat messages from it. 
 - 'timed out': we haven't had any heartbeat messages for some time 
- timeout counter: The number of missed heartbeats left to go. 

The polling loop decrements the timout counter each time it runs and if 
it goes to zero the slave is declared to be timed-out. Each time a  
heartbeat message is received the counter is reset to the value of  
'timeout' from the config dictionary. 
""" 

resource = ''
