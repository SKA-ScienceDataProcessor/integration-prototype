# -*- coding: utf-8 -*-
"""High-level interface for a list of Processing Block (PB) objects."""
import logging

from .config_db_redis import ConfigDb
from .pb import AGGREGATE_TYPE
from .scheduling_object_list import SchedulingObjectList

LOG = logging.getLogger('SIP.EC.CDB')
DB = ConfigDb()


class ProcessingBlockList(SchedulingObjectList):
    """Configuration Database Processing Block List API."""

    def __init__(self):
        """Initialise variables."""
        SchedulingObjectList.__init__(self, AGGREGATE_TYPE)
