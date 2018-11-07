# coding=utf-8
"""High-level interface for subarray objects."""
import logging
from typing import List

from .config_db_redis import ConfigDb
from .subarray import Subarray

DB = ConfigDb()
LOG = logging.getLogger('SIP.EC.CDB')
NUM_SUBARRAYS = 16


class SubarrayList:
    """List of Subarrays."""

    def __init__(self):
        """Initialise the subarray list."""
        LOG.debug("Initialising subarray list.")
        for i in range(NUM_SUBARRAYS):
            Subarray(i)

    @property
    def size(self) -> int:
        """Return the number of subarrays."""
        return NUM_SUBARRAYS

    @property
    def active(self) -> List[str]:
        """Return the list of active subarrays."""
        return self.get_active()

    @property
    def num_active(self) -> int:
        """Return the number of active subarrays."""
        return len(self.get_active())

    @property
    def inactive(self) -> List[str]:
        """Return the list of inactive subarrays."""
        return self.get_inactive()

    @property
    def num_inactive(self) -> int:
        """Return the number of inactive subarrays."""
        return len(self.get_inactive())

    @staticmethod
    def get_active() -> List[str]:
        """Return the list of active subarrays."""
        active = []
        for i in range(NUM_SUBARRAYS):
            key = Subarray.get_key(i)
            if DB.get_hash_value(key, 'active').upper() == 'TRUE':
                active.append(Subarray.get_id(i))
        return active

    @staticmethod
    def get_inactive() -> List[str]:
        """Return the list of inactive subarrays."""
        inactive = []
        for i in range(NUM_SUBARRAYS):
            key = Subarray.get_key(i)
            if DB.get_hash_value(key, 'active').upper() == 'FALSE':
                inactive.append(Subarray.get_id(i))
        return inactive
