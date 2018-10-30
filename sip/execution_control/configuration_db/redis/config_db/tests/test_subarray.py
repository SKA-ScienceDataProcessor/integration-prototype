# coding=utf-8
"""Tests of the Subarray API."""
from ..subarray import Subarray
from ..config_db_redis import ConfigDb
from ..sbi import SchedulingBlockInstance

DB = ConfigDb()


def test_initialise():
    """Test initialising the subarray list."""
    DB.flush_db()
    subarray = Subarray(0)
    assert not subarray.is_active()


def test_activate_deactivate():
    """Test activating and deactivating a subarray"""
    DB.flush_db()
    subarray = Subarray(0)
    subarray.activate()
    assert subarray.is_active()
    subarray.deactivate()
    assert not subarray.is_active()


def test_add_remove_sbi():
    """Test adding and removing SBIs from the subarray."""
    DB.flush_db()
    subarray = Subarray(0)
    subarray.activate()
    sbi_id_1 = SchedulingBlockInstance.get_id()
    subarray.add_sbi_id(sbi_id_1)
    sbi_ids = subarray.get_sbi_ids()
    assert len(sbi_ids) == 1
    sbi_id_2 = SchedulingBlockInstance.get_id()
    subarray.add_sbi_id(sbi_id_2)
    sbi_ids = subarray.get_sbi_ids()
    assert len(sbi_ids) == 2
    subarray.remove_sbi_id(sbi_id_1)
    sbi_ids = subarray.get_sbi_ids()
    assert len(sbi_ids) == 1
    assert sbi_ids[0] == sbi_id_2
