# coding=utf-8
"""Tango SDP Master."""
__subsystem__ = 'TangoControl'
__service_name__ = 'tango_master'
__version_info__ = (1, 0, 0)
__version__ = '.'.join(map(str, __version_info__))
__service_id__ = ':'.join(map(str, (__subsystem__,
                                    __service_name__,
                                    __version__)))
import logging
LOG = logging.getLogger('sip.tango_control.tango_master')
