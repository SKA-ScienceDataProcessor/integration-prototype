# coding=utf-8
"""SDP Master RESTFul web services application.

Intended as a drop in replacement for the Tango SDP Master Device.
"""
__subsystem__ = 'TangoControl'
__service_name__ = 'rest_sdp_master'
__version_info__ = (1, 0, 0)
__version__ = '.'.join(map(str, __version_info__))
__service_id__ = ':'.join(map(str, (__subsystem__,
                                    __service_name__,
                                    __version__)))
import logging
LOG = logging.getLogger('sip.tc.rest_sdp_master')
