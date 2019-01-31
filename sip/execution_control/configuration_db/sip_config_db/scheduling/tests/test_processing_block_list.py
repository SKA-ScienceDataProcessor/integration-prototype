# -*- coding: utf-8 -*-
"""Tests of the Processing Block List API.

The Processing Block List API gives functions for interfacing with the
list of PBs known to the configuration database.
"""
from .utils import add_mock_sbi_workflow_definitions
from .. import ProcessingBlockList, SchedulingBlockInstance
from ... import ConfigDb
from ...utils.generate_sbi_config import generate_sbi_config

DB = ConfigDb()


def test_create_pb_list_object():
    """Test creating a PB list object."""
    pb_list = ProcessingBlockList()
    assert pb_list is not None


def test_pb_list_properties_and_events():
    """Test PB list methods"""
    DB.flush_db()

    sbi_config = generate_sbi_config(num_pbs=2)
    add_mock_sbi_workflow_definitions(sbi_config)

    sbi = SchedulingBlockInstance.from_config(sbi_config)
    pb_list = ProcessingBlockList()

    active = pb_list.active
    assert active[0] in sbi.processing_block_ids
    assert len(pb_list.active) == 2
    assert not pb_list.completed
    assert not pb_list.aborted
