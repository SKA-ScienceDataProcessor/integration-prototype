# coding=utf-8
"""Processing Controller release info."""
__subsystem__ = 'ExecutionControl'
__service_name__ = 'ProcessingController'
__version_info__ = (1, 2, 3)
__version__ = '.'.join(map(str, __version_info__))
__service_id__ = ':'.join(map(str, (__subsystem__,
                                    __service_name__,
                                    __version__)))
