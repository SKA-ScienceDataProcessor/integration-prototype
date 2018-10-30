# coding=utf-8
"""High-level interface for subarray objects."""
import logging
import ast

from .config_db_redis import ConfigDb

DB = ConfigDb()
LOG = logging.getLogger('SIP.EC.CDB')

OBJECT_PREFIX = 'subarrays'


class Subarray:
    """Subarray API."""

    def __init__(self, subarray_id):
        """Initialise the subarray object."""
        if isinstance(subarray_id, int):
            self.id = self.get_id(subarray_id)
        else:
            self.id = subarray_id
        LOG.debug("Initialising subarray {}.", self.id)
        subarray_config = dict(id=self.id, active=False, parameters={},
                               sbi_ids=[])
        self.key = '{}:{}'.format(OBJECT_PREFIX, self.id)
        if not DB.key_exists(self.key):
            DB.set_hash_values(self.key, subarray_config)

    def get_config(self):
        """Return the subarray configuration.

        Returns:
            dict, the subarray configuration

        """
        return DB.get_hash_dict(self.key)

    def set_config(self, config_dict):
        """Set the subarray configuration."""

    def activate(self):
        """Activate the subarray."""
        DB.set_hash_value(self.key, 'active', 'true')

    def deactivate(self):
        """Deactivate the subarray."""
        DB.set_hash_value(self.key, 'active', 'false')

    def get_sbi_ids(self):
        """Get the list of SBI Ids.

        Returns:
            list, list of SBI ids associated with this subarray.

        """
        return ast.literal_eval(DB.get_hash_value(self.key, 'sbi_ids'))

    def add_sbi_id(self, sbi_id):
        """Add a SBI Identifier."""
        if not self.is_active():
            raise RuntimeError("Unable to add SBIs to inactive subarray!")
        sbi_ids = self.get_sbi_ids()
        sbi_ids.append(sbi_id)
        DB.set_hash_value(self.key, 'sbi_ids', sbi_ids)

    def remove_sbi_id(self, sbi_id):
        """Remove an SBI Identifier."""
        sbi_ids = self.get_sbi_ids()
        sbi_ids.remove(sbi_id)
        DB.set_hash_value(self.key, 'sbi_ids', sbi_ids)

    def is_active(self) -> bool:
        """Return True if the subarray is active, otherwise False.

        Returns:
            bool, True if the subarray is active, otherwise False

        """
        value = DB.get_hash_value(self.key, 'active')
        return True if value == 'true' else False

    @staticmethod
    def get_id(index: int):
        """Convert a subarray index into a subarray id.

        Returns:
            str, the subarray id for the specified index

        """
        return 'subarray_{:02d}'.format(index)

    @staticmethod
    def get_key(index: int):
        """Get the subarray key for a given index.

        Returns:
            str, the subarray key

        """
        return '{}:{}'.format(OBJECT_PREFIX, Subarray.get_id(index))
