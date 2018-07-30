# -*- coding: utf-8 -*-
"""Tests of the Config db client API Processing Controller resources.

For instructions of how to run these tests see the README.md file in the
`sip/configuration_db/redis` folder.

TODO(BM)
    - Remove generator functions
    - Make functions more specific wrt resources
        - get_block_details
        - update_value
        - events
    - Move events to another module?
    - Add methods to genereate ids (eg. sub_array_ids etc)
    - Update sub-array interfaces to respect time

"""
import datetime
import pytest
import jsonschema

from ..processing_controller_client import ProcessingControllerDbClient


def test_create_client_object():
    """Test creating a client object."""
    db_client = ProcessingControllerDbClient()
    assert db_client is not None


def test_get_sbi_id():
    """Test method to generate a valid SBI id."""
    db_client = ProcessingControllerDbClient()
    db_client.clear()

    sbi_id = db_client.get_sbi_id()
    now = datetime.datetime.utcnow()
    assert sbi_id == '{}-sip-sbi000'.format(now.strftime('%Y%m%d'))

    sbi_id = db_client.get_sbi_id(project='test')
    now = datetime.datetime.utcnow()
    assert sbi_id == '{}-test-sbi000'.format(now.strftime('%Y%m%d'))

    sbi_id = db_client.get_sbi_id(date='20180101')
    assert sbi_id == '20180101-sip-sbi000'

    sbi_id = db_client.get_sbi_id(datetime.datetime(2018, 3, 2))
    assert sbi_id == '20180302-sip-sbi000'


def test_scheduling_blocks():
    """Test Scheduling Block Instance resource functions."""
    db_client = ProcessingControllerDbClient()
    db_client.clear()

    # Add a block with an invalid schema.
    with pytest.raises(jsonschema.ValidationError,
                       match=r'^\'id\' is a required'):
        db_client.add_scheduling_block({})

    # Add a block with valid schema
    config1 = dict(id="20180110-sip-sbi000",
                   scheduling_block_id="20180101-sip-sb000",
                   sub_array_id="subarray-00",
                   processing_blocks=[])
    db_client.add_scheduling_block(config1)
    assert db_client.get_num_scheduling_blocks() == 1
    assert db_client.get_scheduling_block_ids() == [config1['id']]

    # Add a second block with valid schema
    config2 = dict(id="20180531-sip-sbi001",
                   scheduling_block_id="20180531-sip-sb000",
                   sub_array_id="subarray-00",
                   processing_blocks=[])
    db_client.add_scheduling_block(config2)
    assert db_client.get_num_scheduling_blocks() == 2
    block_ids = db_client.get_scheduling_block_ids()
    assert block_ids == [config1['id'], config2['id']]

    # Query the details of the 1st block.
    sbi_config = db_client.get_block_details([config1['id']]).__next__()
    assert sbi_config['id'] == config1['id']
    assert sbi_config['sub_array_id'] == config1['sub_array_id']

    # Query the details of the 2nd block.
    sbi_config = db_client.get_block_details([config2['id']]).__next__()
    assert sbi_config['id'] == config2['id']
    assert sbi_config['sub_array_id'] == config2['sub_array_id']

    # Test adding duplicate blocks (1st block again)
    # FIXME(BM) Adding duplicate SBIs should fail or raise an exception?
    db_client.add_scheduling_block(config1)
    assert db_client.get_num_scheduling_blocks() == 2

    # Delete the first scheduling block and verify
    db_client.delete_scheduling_block(config1['id'])
    assert db_client.get_num_scheduling_blocks() == 1
    block_ids = db_client.get_scheduling_block_ids()
    assert block_ids == [config2['id']]

    # Check deleting a missing / invalid SBI
    with pytest.raises(KeyError, match='Scheduling Block Instance not found'):
        db_client.delete_scheduling_block('foo')

    #  Update the status (or any other field) of the SBI
    sbi = db_client.get_block_details(config2['id']).__next__()
    assert 'status' in sbi
    assert sbi['status'] == 'created'
    db_client.update_value(config2['id'], 'status', 'TEST')
    sbi = db_client.get_block_details(config2['id']).__next__()
    assert sbi['status'] == 'TEST'

    # Get the latest scheduling block event
    event = db_client.get_latest_event('scheduling_block')
    assert event['type'] == 'deleted'
    assert event['id'] == config1['id']

    # Get the next latest event from the event stack
    event = db_client.get_latest_event('scheduling_block')
    assert event['type'] == 'created'
    assert event['id'] == config1['id']


def test_processing_blocks():
    """Test Processing Block resource functions."""
    db_client = ProcessingControllerDbClient()
    db_client.clear()

    # Add a block with valid schema
    config1 = dict(id="20180101-sip-sbi000",
                   scheduling_block_id="20180101-sip-sb000",
                   sub_array_id="subarray-00",
                   processing_blocks=[
                       dict(id='sip-pb000',
                            resources_requirement=dict(),
                            workflow=dict()),
                       dict(id='sip-pb001',
                            resources_requirement=dict(),
                            workflow=dict()),
                   ])
    db_client.add_scheduling_block(config1)
    assert db_client.get_num_processing_blocks() == 2
    pb_ids = db_client.get_processing_block_ids()
    assert pb_ids == [config1['processing_blocks'][0]['id'],
                      config1['processing_blocks'][1]['id']]
    pb1 = db_client.get_block_details(config1['processing_blocks'][1]['id'])
    pb1 = pb1.__next__()
    assert pb1['id'] == config1['processing_blocks'][1]['id']

    # Try to add another block with duplicate PB ids
    config2 = dict(id="20180101-sip-sbi001",
                   scheduling_block_id="20180101-sip-sb000",
                   sub_array_id="subarray-00",
                   processing_blocks=[dict(id='sip-pb000',
                                           resources_requirement=dict(),
                                           workflow=dict())])
    with pytest.raises(Exception, match='Processing block already exists'):
        db_client.add_scheduling_block(config2)

    # Add another block with new PBs
    config2 = dict(id="20180101-sip-sbi001",
                   scheduling_block_id="20180101-sip-sb000",
                   sub_array_id="subarray-00",
                   processing_blocks=[
                       dict(id='sip-pb002', resources_requirement={},
                            workflow={}),
                       dict(id='sip-pb003', resources_requirement={},
                            workflow={})
                   ])
    db_client.add_scheduling_block(config2)
    assert db_client.get_num_processing_blocks() == 4
    pb_ids = db_client.get_processing_block_ids()
    assert 'sip-pb003' in pb_ids
    assert pb_ids[2] == 'sip-pb002'

    # Get the details of a Processing Block
    pb_data = db_client.get_block_details(
        config2['processing_blocks'][0]['id'])
    pb_data = pb_data.__next__()
    assert pb_data['id'] == config2['processing_blocks'][0]['id']
    assert 'workflow' in pb_data
    assert 'resources_requirement' in pb_data
    assert 'status' in pb_data
    assert pb_data['status'] == 'created'

    # Update the status (or another key) of the PB
    db_client.update_value(pb_data['id'], 'status', 'TEST')
    pb_data = db_client.get_block_details(pb_data['id']).__next__()
    assert pb_data['status'] == 'TEST'

    # Delete an invalid / missing PB
    with pytest.raises(KeyError, match='Processing Block not found'):
        db_client.delete_processing_block('foo')

    # Delete a PB
    db_client.delete_processing_block(pb_data['id'])
    assert db_client.get_num_processing_blocks() == 3

    # Get the latest event
    event = db_client.get_latest_event('processing_block')
    assert event['type'] == 'deleted'
    assert event['id'] == pb_data['id']


def test_sub_arrays():
    """Test Sub-array resource methods."""
    db_client = ProcessingControllerDbClient()
    db_client.clear()

    # Add some scheduling blocks
    date = datetime.datetime(2018, 1, 1)
    sb_id = "20180101-sip-sb000"
    config1 = dict(id=db_client.get_sbi_id(date=date),
                   scheduling_block_id=sb_id,
                   sub_array_id="subarray-00",
                   processing_blocks=[])
    db_client.add_scheduling_block(config1)
    config2 = dict(id=db_client.get_sbi_id(date=date),
                   scheduling_block_id=sb_id,
                   sub_array_id="subarray-01",
                   processing_blocks=[])
    db_client.add_scheduling_block(config2)
    config3 = dict(id=db_client.get_sbi_id(date=date),
                   scheduling_block_id=sb_id,
                   sub_array_id="subarray-00",
                   processing_blocks=[])
    db_client.add_scheduling_block(config3)
    assert db_client.get_num_scheduling_blocks() == 3

    # Check that the list of (active) subarrays is correct.
    sb_ids = db_client.get_sub_array_ids()
    assert sb_ids == ['subarray-00', 'subarray-01']

    # Get the SBIs for the specified subarray
    sbi_ids = db_client.get_sub_array_sbi_ids('subarray-00')
    assert sbi_ids == ['20180101-sip-sbi000', '20180101-sip-sbi002']

    # Get the SBIs for the specified subarray
    sbi_ids = db_client.get_sub_array_sbi_ids('subarray-01')
    assert sbi_ids == ['20180101-sip-sbi001']
