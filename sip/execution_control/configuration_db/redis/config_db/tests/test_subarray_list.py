# coding=utf-8
"""Tests of the SubarrayList API."""
from ..subarray_list import SubarrayList
from ..subarray import Subarray
from ..config_db_redis import ConfigDb

DB = ConfigDb()


def test_initialise():
    """Test initialising the subarray list."""
    DB.flush_db()
    subarray_list = SubarrayList()
    # No subarrays should be active.
    assert not subarray_list.get_active()


def test_get_activate():
    """Test subarray activation."""
    DB.flush_db()
    Subarray(2).activate()
    subarray_list = SubarrayList()
    # Only subarray 2 should now be active
    active = subarray_list.get_active()
    assert len(active) == 1
    assert active[0] == Subarray.get_id(2)
