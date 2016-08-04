""" Integration prototype resource manager

__author__ = David Terrett
"""

class ResourceManager:
    """ Resource manager class
    """
    def __init__(self, host_props):

        # Create host properties dictionary. This contains the characteristics
        # of every host.
        self._host_props = host_props

        # Create allocation dictionary with an empty entry for every host in
        # the properties dictionary. This tracks the resource allocations
        # for each host.
        self._host_alloc = {}
        for host in host_props:
            self._host_alloc[host] = {}

        # Create empty task dictionary. This maps tasks to the host they have
        # been allocated.
        self._task_dict = {}

    def allocate_host(self, task_name, req_props, des_props):
        """ Allocate a host for a task
        """
        if task_name in self._task_dict:
            raise RuntimeError(
                    'task entry already exists in the task dictionary')

        # Find a suitable host
        host = self._select_host(task_name, req_props, des_props)

        # Set the host name in the task dictionary
        self._task_dict[task_name] = host

        # Create a tcp port entry for this host in the allocation dictionary
        # if it doesn't already exist.
        if not 'tcp_port' in self._host_alloc[host]:
            self._host_alloc[host]['tcp_port'] = []

        return host

    def allocate_resource(self, task_name, resource_type):
        """ Allocate a resource

        If the task hasn't been allocated a host, an exception is raised
        """
        if not task_name in self._task_dict:
            raise RuntimeError("Resources can't be allocated before a host")

        if resource_type == 'tcp_port':
            return self._allocate_tcp_port(self._task_dict[task_name], 
                    task_name)
        else:
            raise RuntimeError('Resource type "' + resource_type + 
                    '" not recognised')

    def release_host(self, task_name):
        """ Deallocate a task's host
        """

        # Get the name of the host from the task dictionary.
        host = self._task_dict[task_name]

        # Delete the entry.
        del self._task_dict[task_name]

        # Remove the task from the list of tasks the host is allocated to.
        self._host_alloc[host]['tasks'].remove(task_name)

        # Release any tcp ports allocated to this task.
        self._release_tcp_ports(host, task_name)

    def sip_root(self, host):
        """ Returns the path to the root of the SIP on the specified host
        """
        return self._host_props[host]['sip_root']
    
    def _allocate_tcp_port(self, host, task_name):

        # Search the port range for an used port on this host
        for port in range(6000, 7000):
            if self._port_is_free(host, port):

                # Add this port to the list of allocated ports for this host
                self._host_alloc[host]['tcp_port'].append((port, task_name))
                return port
        raise RuntimeError('No free ports on host "' + host + '"')

    def _host_is_suitable(self, host, req_props):
        """ Checks if host matches the required properties

        Returns the host name if it is and False otherwise
        """

        # The host must be in the host properties list
        if host in self._host_props:
            #host_props = self._host_props[host]

            # If the exclusive flag is set for this host we can't allocate
            # it to any more tasks.
            if self._host_alloc[host].get('exclusive', False):
                return False

            # Go through all the required properties checking that it is
            # satisfied by the host.
            for prop, value in req_props.items():

                # Check that the host names match
                if prop == 'host':
                    if host != value:
                        return False

                # Check that the launch protocol is in the list
                elif prop == 'launch_protocol':
                    if not value in self._host_props[host]['launch_protocol']:
                        return False

                # If exclusive access is requested, check that there are no 
                # other tasks allocated to this host
                elif prop == 'exclusive':
                   if value:
                       if 'tasks' in self._host_alloc[host]:
                            return False
            return host
        else:
            return False

    def _port_is_free(self, host, port):
        for entry in self._host_alloc[host]['tcp_port']:
            if entry[0] == port:
                return False
        return True

    def _release_tcp_ports(self, host, task_name):
        new_list = []
        for entry in self._host_alloc[host]['tcp_port']:
            if entry[1] != task_name:
                new_list.append(entry)
        self._host_alloc[host]['tcp_port'] = new_list

    def _select_host(self, task, req_props, des_props):
        """ Find a host that matches the required properties

        A host assigned to the fewest tasks is selected.

        Raises an exception if there is no suitable host available
        """

        # If a named host is required then just return that (if it is suitable).
        if 'host' in req_props:
            host = req_props['host']
            if not self._host_is_suitable(host, req_props):
                raise RuntimeError(
                        'specified host does not have the required properties')
        else:
            
            # Look for a suitable host that doesn't isn't allocated to a task
            # yet. Any suitable hosts that do have a task allocated are added
            # to a backup list in case there are none to be found.
            backup_host = ''
            for host, alloc in self._host_alloc.items():
                if self._host_is_suitable(host, req_props):

                    # If the task list is empty use this host
                    allocated_tasks = len(alloc.get('tasks', []))
                    if allocated_tasks == 0:
                        backup_host = ''
                        break;
                    else:
                        if backup_host == '':
                            backup_host = host
                            backup_allocated_tasks = allocated_tasks
                        elif allocated_tasks < backup_allocated_tasks:
                            backup_host = host
                            backup_allocated_tasks = allocated_tasks

            # If backup_host is set it means that we didn't find a host not
            # allocated to any task.
            if backup_host != '':
                host = backup_host

        # Add this task to the list of tasks this has been allocated to.
        if not 'tasks' in self._host_alloc[host]:
            self._host_alloc[host]['tasks'] = []
        self._host_alloc[host]['tasks'].append(task)

        # If exclusive access is requested, set the exclusive flag in the
        # host allocation dictionary.
        if req_props.get('exclusive', False):
            self._host_alloc[host]['exclusive'] = True
        return host
