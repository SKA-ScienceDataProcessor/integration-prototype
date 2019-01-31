# coding=utf-8
"""Release information for the SIP Execution Control Configuration Database."""
__version_info__ = (1, 3, 0, 'a1')
__version__ = '.'.join(map(str, __version_info__[0:3]))
if len(__version_info__) == 4:
    __version__ += __version_info__[3]
__num_subarrays__ = 16
