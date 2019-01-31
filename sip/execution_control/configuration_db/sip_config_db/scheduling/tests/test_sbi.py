# -*- coding: utf-8 -*-
"""Tests of the Scheduling Block Instance API."""
import datetime
import pytest

from .utils import add_mock_sbi_workflow_definitions
from .. import SchedulingBlockInstance
from ... import ConfigDb
from ...utils.generate_sbi_config import generate_sbi_config

DB = ConfigDb()


def test_sbi_get_id():
    """Test static method to generate a valid SBI id."""
    DB.flush_db()

    utc_now = datetime.datetime.utcnow()

    sbi_id = SchedulingBlockInstance.generate_sbi_id()
    assert sbi_id.startswith('SBI-')

    instance_id = 1
    sbi_id = SchedulingBlockInstance.generate_sbi_id(utc_now, project='sip',
                                                     instance_id=instance_id)
    assert sbi_id == 'SBI-{}-sip-{:04d}'.format(utc_now.strftime('%Y%m%d'),
                                                instance_id)
    sbi_id = SchedulingBlockInstance.generate_sbi_id(utc_now, project='test',
                                                     instance_id=0)
    assert sbi_id == 'SBI-{}-test-0000'.format(utc_now.strftime('%Y%m%d'))

    sbi_id = SchedulingBlockInstance.generate_sbi_id(date='20180101',
                                                     instance_id=0)
    assert sbi_id == 'SBI-20180101-sip-0000'

    sbi_id = SchedulingBlockInstance.generate_sbi_id(
        datetime.datetime(2018, 3, 2), instance_id=12345)
    assert sbi_id == 'SBI-20180302-sip-12345'


def test_sbi_from_config():
    """Test creating an SBI from a configuration dictionary."""
    DB.flush_db()

    # Test normal usage.
    sbi_config = generate_sbi_config(num_pbs=2)
    add_mock_sbi_workflow_definitions(sbi_config)
    sbi = SchedulingBlockInstance.from_config(sbi_config)
    assert sbi.id == sbi_config['id']
    assert sbi.num_pbs == 2

    # Adding an SBI with an unknown workflow definition should fail.
    sbi_config = generate_sbi_config(num_pbs=1)
    with pytest.raises(KeyError, message='Unknown workflow definition'):
        SchedulingBlockInstance.from_config(sbi_config)

    # Check that adding an SBI with an existing PB (id) fails.
    sbi_config = generate_sbi_config(num_pbs=1)
    add_mock_sbi_workflow_definitions(sbi_config)
    sbi_config['processing_blocks'][0]['id'] = sbi.processing_block_ids[0]
    with pytest.raises(KeyError,
                       message="PB '{}' already exists!".format(
                           sbi.processing_block_ids[0])):
        SchedulingBlockInstance.from_config(sbi_config)

    # Test undefined workflow
    sbi_config = generate_sbi_config(num_pbs=1)
    with pytest.raises(KeyError, match=r'Unknown workflow definition'):
        SchedulingBlockInstance.from_config(sbi_config)
