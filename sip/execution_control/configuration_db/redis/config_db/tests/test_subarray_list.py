# coding=utf-8
"""Tests of the SubarrayList API."""
from ..subarray_list import SubarrayList, DB
from ..subarray import Subarray


def test_initialise():
    """Test initialising the subarray list."""
    DB.flush_db()
    subarray_list = SubarrayList()
    # No subarrays should be active.
    assert not subarray_list.active


def test_get_activate():
    """Test subarray activation."""
    DB.flush_db()
    Subarray(2).activate()

    subarray_list = SubarrayList()

    # Only subarray 2 should now be active
    assert subarray_list.num_active == 1
    assert subarray_list.active[0] == Subarray.get_id(2)

    assert subarray_list.num_inactive == subarray_list.size - 1
    assert subarray_list.inactive[0] == Subarray.get_id(0)
