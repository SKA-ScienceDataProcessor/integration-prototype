# coding=utf-8
"""SIP Execution Control Configuration Database client library."""
__version_info__ = (1, 1, 0)
__version__ = '.'.join(map(str, __version_info__))
__logger_name__ = 'sip.ec.config_db'
import logging
from ._config_db_redis import ConfigDb, flush_db
LOG = logging.getLogger(__logger_name__)
DB = ConfigDb()
__all__ = [
    '__version_info__',
    '__version__',
    'flush_db',
    'DB'
]
