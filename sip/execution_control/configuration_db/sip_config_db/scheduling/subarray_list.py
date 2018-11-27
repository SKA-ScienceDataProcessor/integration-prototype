# coding=utf-8
"""High-level interface for subarray objects."""
from typing import List

from .subarray import Subarray
from .. import ConfigDb
from ..release import __num_subarrays__

DB = ConfigDb()


class SubarrayList:
    """List of Subarrays."""

    def __init__(self):
        """Initialise the subarray list."""
        for i in range(__num_subarrays__):
            Subarray(i)

    @property
    def size(self) -> int:
        """Return the number of subarrays."""
        return __num_subarrays__

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
        for i in range(__num_subarrays__):
            key = Subarray.get_key(i)
            if DB.get_hash_value(key, 'active').upper() == 'TRUE':
                active.append(Subarray.get_id(i))
        return active

    @staticmethod
    def get_inactive() -> List[str]:
        """Return the list of inactive subarrays."""
        inactive = []
        for i in range(__num_subarrays__):
            key = Subarray.get_key(i)
            if DB.get_hash_value(key, 'active').upper() == 'FALSE':
                inactive.append(Subarray.get_id(i))
        return inactive
