"""Global configuration.

This file defines the master control global data.
"""

master_controller_state_machine = None
logserver = None

resource = None
"""Resource manager."""

_slave_config_dict = {}
"""Slave config.

This dictionary defines the properties of all the slave controllers that 
we might want to start. It is indexed by the slave 'name' (just some 
arbitrary string) and each entry is a dictionary containing at least the 
following 
 
- The 'launch policy' of the slave. This allows the master control to use the 
  appropriate method to start the slave 
- 'online' specifies whether or not the slave should be running as a service
  when the master controller is on line.
  
Other stuff in the entry contains the info need to start the slave.
""" 

_slave_status_dict = {}
"""Slave status.

This dictionary the state and other information about the slaves that is
only known at run time.. 

It includes:
- "type": the slave type; an index into the slave config.
- "task_controller": The SlaveTaskController object that can send commands
to the slave
- "state": The state machine that shadows the state of the slave controller
- "descriptor": The PAAS descriptor for the slave controller service.
""" 

def slave_status(name):
    """ Get slave status dictionary.

    Returns the status dictionary for the specified slave
    """
    if name in _slave_status_dict:
        return _slave_status_dict[name]
    return None

def slave_config(name):
    """ Get slave config dictionary.

    Returns the config dictionary for the specified slave. Note that the
    name is not the slave type but the slave name.
    """
    if name in _slave_status_dict:
        return _slave_config_dict[_slave_status_dict[name]['type']]
    return None

def create_slave_status(name, type, task_controller, state_machine):
    """ Create new entry in the slave status dictionary
    """
    if not name in _slave_status_dict:
        if type not in _slave_config_dict:
            raise RuntimeError('"{}" is not known task type'.format(type))
        _slave_status_dict[name] = {
            'type': type,
            'task_controller': task_controller,
            'state': state_machine,
            'descriptor': None}


def slave_status_dict():
    """ Returns the slave status dictionary.
    """
    return _slave_status_dict


def slave_config_dict():
    """ Returns the slave config dictionary.
    """
    return _slave_config_dict
