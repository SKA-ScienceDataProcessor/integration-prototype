""" Slave map
This dictionary defines the properties of all the slave controllers that
we might want to start. It is indexed by the slave 'name' (just some
arbitrary string) and each entry is a dictionary containing at least the
following

- The 'type' of the slave. This allows the master control to use the
  appropriate method to start the slave
- slave's state, which can be one:	
	- an empty string: Either we have never tried to start the slave or we have shut it down cleanly.
	- 'running': we managed to start the slave and we are receiving heartbeat messages from it.
	- 'timed out': we haven't had any heartbeat messages for some time
	
- 'timeout': The number of polling intervals we are prepared to not
  see a heartbeat message for before declaring the slave awol.
- timeout counter: The number of missed heartbeats left to go.

The polling loop decrements the timout counter each time it runs and if
it goes to zero the slave is declared to be timed-out. Each time a 
heartbeat message is received the counter is reset to the value of 
'timeout'.

Other stuff in the entry contains the info need to start the slave (e.g.
what host it should run on).
"""
__author__ = 'David Terrett'

slave_map = {}
slave_map['LTS'] = {'state':'', 
                    'new_state':'',
                    'type': 
                    'docker', 
                    'timeout': 10, 
                    'timeout counter': 0, 
                    'engine_url': 'unix:///var/run/docker.sock', 
                    'image': 'slave_controller',
                    'host': 'localhost',
                    'heartbeat_port': '6477',
                    'rpc_port': '6479'}
