# -*- coding: utf-8 -*-
"""High-level interface for Scheduling Block Instance (SBI) objects."""
import logging
import os

from .config_db_redis import ConfigDb
from .sbi import AGGREGATE_TYPE, SchedulingBlockInstance
from .scheduling_object_list import SchedulingObjectList

LOG = logging.getLogger('SIP.EC.CDB')
DB = ConfigDb()


class SchedulingBlockInstanceList(SchedulingObjectList):
    """Configuration Database client API for Scheduling Block Instances."""

    def __init__(self, schema_path=None):
        """Initialise variables."""
        SchedulingObjectList.__init__(self, AGGREGATE_TYPE)

        if schema_path is None:
            schema_path = os.path.join(os.path.dirname(__file__), 'schema',
                                       'sbi_configure_schema.json')
        self._schema_path = schema_path

    def add(self, sbi_config: dict,
            subarray_id: str = None) -> SchedulingBlockInstance:
        """Add Scheduling Block Instance to the database.

        Args:
            sbi_config (dict): SBI configuration dictionary.
            subarray_id (str, optional): Subarray id

        Returns:
            SchedulingBlockInstance

        Raises:
            ValidationError, if the supplied config_dict is invalid.
            RuntimeError, if a PB workflow definition (id, version) is not
            known.

        """
        return SchedulingBlockInstance.from_config(sbi_config, subarray_id,
                                                   self._schema_path)
