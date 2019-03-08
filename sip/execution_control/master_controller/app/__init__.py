# coding=utf-8
"""SIP Execution Control Master Controller."""
__subsystem__ = 'ExecutionControl'
__service_name__ = 'MasterController'
__version_info__ = (1, 3, 0)
__version__ = '.'.join(map(str, __version_info__))
__service_id__ = ':'.join(map(str, (__subsystem__,
                                    __service_name__,
                                    __version__)))
import logging
LOG = logging.getLogger('sip.ec.master_controller')
