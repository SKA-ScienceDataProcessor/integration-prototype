# coding=utf-8
"""SIP Prometheus Alarm Receiver."""
__subsystem__ = 'Platform.Alarms.Prometheus'
__service_name__ = 'AlarmReceiver'
__version_info__ = (1, 0, 0)
__version__ = '.'.join(map(str, __version_info__))
__service_id__ = ':'.join(map(str, (__subsystem__,
                                    __service_name__,
                                    __version__)))

