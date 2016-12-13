import threading

from sip_common import logger
from sip_master import config
from sip_master import slave_control

"""A thread class that is run when a capability is started."""
__author__ = 'David Terrett'


class Capability(threading.Thread):
    """Does the actual work of starting a capability."""

    def __init__(self, *args):
        super(Capability, self).__init__()
        # args[0] is capability name, which must be unique.
        # args[1] is capability type, used to select from list in slave_map.
        # If there is only one capability of this type,
        # name and type can be the same.
        self._args = args

    def run(self):
        """Thread run routine."""
        logger.info('starting capability {} with name {}'.format(
            self._args[1], self._args[0]))
        try:
            slave_control.start(self._args[0], self._args[1])
        except RuntimeError as err:
            logger.error('Failed to start capability: {}'.format(err))
