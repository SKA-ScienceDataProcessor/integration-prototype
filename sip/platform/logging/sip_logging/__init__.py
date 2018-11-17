# coding: utf-8
"""SIP logging module."""
__version_info__ = (1, 0, 12)
__version__ = '.'.join(map(str, __version_info__))
from .sip_logging import init_logger
__all__ = ['init_logger']
