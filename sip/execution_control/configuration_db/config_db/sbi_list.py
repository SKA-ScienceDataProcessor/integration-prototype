# -*- coding: utf-8 -*-
"""High-level interface for Scheduling Block Instance (SBI) objects."""
import logging

from .config_db_redis import ConfigDb
from .sbi import AGGREGATE_TYPE, SchedulingBlockInstance
from .scheduling_object_list import SchedulingObjectList

LOG = logging.getLogger('SIP.EC.CDB')
DB = ConfigDb()


class SchedulingBlockInstanceList(SchedulingObjectList):
    """Configuration Database client API for Scheduling Block Instances."""

    def __init__(self):
        """Initialise variables."""
        SchedulingObjectList.__init__(self, AGGREGATE_TYPE)

    @staticmethod
    def add(sbi_config: dict) -> SchedulingBlockInstance:
        """Add Scheduling Block Instance to the database.

        Args:
            sbi_config (dict): SBI configuration dictionary.

        Returns:
            SchedulingBlockInstance

        Raises:
            ValidationError, if the supplied config_dict is invalid.
            RuntimeError, if a PB workflow definition (id, version) is not
            known.

        """
        return SchedulingBlockInstance.from_config(sbi_config)
