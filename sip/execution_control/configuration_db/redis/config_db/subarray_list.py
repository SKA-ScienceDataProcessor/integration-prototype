# coding=utf-8
"""High-level interface for subarray objects.

FIXME(BM): Needs the following methods:
    * __init__(id) : initialise subarrays in the database
    * activate(id) : activate a subarray
    * get(active=true|false) : get subarray paramters
    * deactivate(id) : deactivate a subarray
    * abort(id)
    * get_pb_list(id)
    * get_sbi_list()
    * state()
    * version()

    * __init__() : initialise all subarrays in the database
    * activate(id) : activate a subarray
    * deactivate(id) : deactivate a subarray
    * get(active=true|false) : get list of active/inactive subarrays
    * abort(id)
    * get_subarray(id): return subarray object for given id
"""
from typing import Union
import logging
from .config_db_redis import ConfigDb
from .subarray import Subarray, OBJECT_PREFIX

DB = ConfigDb()
NUM_SUBARRAYS = 16
LOG = logging.getLogger('SIP.EC.CDB')


class SubarrayList:
    """."""

    _key_prefix = OBJECT_PREFIX

    def __init__(self):
        """Initialise the subarray list"""
        LOG.debug("Initialising subarray list.")
        for i in range(NUM_SUBARRAYS):
            Subarray(i)

    @staticmethod
    def length():
        """Return the number of subarrays."""
        return NUM_SUBARRAYS

    @staticmethod
    def get_config(subarray_id: Union[int, str]):
        """Return a subarray configuration.

        Args:
            subarray_id (str): string
        """
        return Subarray(subarray_id).get_config()

    @staticmethod
    def get_active():
        """Return the list of active subarrays."""
        active = []
        for i in range(NUM_SUBARRAYS):
            key = Subarray.get_key(i)
            if DB.get_hash_value(key, 'active') == 'true':
                active.append(Subarray.get_id(i))
        return active

    @staticmethod
    def get_inactive():
        """Return the list of inactive subarrays."""
        inactive = []
        for i in range(NUM_SUBARRAYS):
            key = Subarray.get_key(i)
            if DB.get_hash_value(key, 'active') == 'false':
                inactive.append(Subarray.get_id(i))
        return inactive


    @staticmethod
    def activate(subarray_id: Union[int, str]):
        """Activate the specified subarray.

        Args:
            subarray_id (str): string
        """
        Subarray(subarray_id).activate()

    @staticmethod
    def deactivate(subarray_id: Union[int, str]):
        """Deactivate the specified subarray.

        Args:
            subarray_id (str): string
        """
        Subarray(subarray_id).deactivate()


