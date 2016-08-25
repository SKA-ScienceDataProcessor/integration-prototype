""" Functions executed when a capability is started
"""
__author__ = 'David Terrett'

import threading 

from sip_common import logger
from sip_master import config
from sip_master import slave_control

class Capability(threading.Thread):
    """ Does the actual work of starting a capability
    """
    def __init__(self, *args):
        super(Capability, self).__init__()
        self._args = args

    def run(self):
        """ Thread run routine
        """
        logger.info('starting capability ' + self._args[0])

        slave_control.start(self._args[0], self._args[1])
