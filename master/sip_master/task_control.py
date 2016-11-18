""" Functions for comanding a slave controller to load and unload tasks
"""

import os
import rpyc

from sip_master import config
from sip_common import logger


class TaskController:
    def __init__(self):
        pass

    def shutdown(self):
        """Command the slave controller to shut down."""
        pass

    def start(self, name, cfg, status):
        """Command the slave controller to load a task."""
        pass

    def stop(self, cfg):
        """Command the slave controller to unload the task."""
        pass


class TaskControllerRPyC(TaskController):
    def __init__(self):
        TaskController.__init__(self)
        self._conn = None

    def connect(self, address, port):
        """Establishes an RPyC connection if it is not already."""
        if self._conn is None:
            self._conn = rpyc.connect(address, port)

    def shutdown(self):
        """Command the slave controller to shut down."""
        if self._conn is None:
            logger.fatal("Need to connect to RPyC first!")
            return
        self._conn.root.shutdown()

    def start(self, name, cfg, status):
        """Command the slave controller to load a task."""
        # Scan the task parameter list for entries with values starting with a #
        # character and replace with an allocated resource.
        task_cfg = cfg['task']
        for k, v in enumerate(task_cfg):
            if v[0] == '#':
                task_cfg[k] = str(
                    config.resource.allocate_resource(name, v[1:]))

        # Update the task executable (the first element of the list) to an
        # absolute path
        task_cfg[0] = os.path.join(status['sip_root'], task_cfg[0])

        # Send the slave the command to load the task
        if self._conn is None:
            logger.fatal("Need to connect to RPyC first!")
            return
        self._conn.root.load(task_cfg)

    def stop(self, cfg):
        """Command the slave controller to unload the task."""
        if self._conn is None:
            logger.fatal("Need to connect to RPyC first!")
            return
        self._conn.root.unload(cfg['task'])

