# -*- coding: utf-8 -*-
"""SIP Tango Processing Device package."""
import logging
__subsystem__ = 'TangoControl'
__service_name__ = 'ProcessingBlock'
__version_info__ = (1, 2, 0)
__version__ = '.'.join(map(str, __version_info__))
__service_id__ = ':'.join(map(str, (__subsystem__,
                                    __service_name__,
                                    __version__)))
LOG = logging.getLogger('sip.tc.processing_block')
__all__ = [
    '__subsystem__',
    '__service_name__',
    '__version__',
    '__service_id__',
    'LOG'
]
