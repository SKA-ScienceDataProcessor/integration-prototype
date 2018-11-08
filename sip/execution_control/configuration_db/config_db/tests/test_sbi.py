# -*- coding: utf-8 -*-
"""Tests of the Scheduling Block Instance API."""
import datetime

from .workflow_test_utils import add_test_sbi_workflow_definitions
from ..sbi import DB, SchedulingBlockInstance
from ..utils.generate_sbi_configuration import generate_sbi_config


def test_sbi_get_id():
    """Test static method to generate a valid SBI id."""
    DB.flush_db()
    utc_now = datetime.datetime.utcnow()
    instance_id = 1
    sbi_id = SchedulingBlockInstance.get_id(utc_now, project='sip',
                                            instance_id=instance_id)
    assert sbi_id == 'SBI-{}-sip-{:04d}'.format(utc_now.strftime('%Y%m%d'),
                                                instance_id)
    sbi_id = SchedulingBlockInstance.get_id(utc_now, project='test',
                                            instance_id=0)
    assert sbi_id == 'SBI-{}-test-0000'.format(utc_now.strftime('%Y%m%d'))

    sbi_id = SchedulingBlockInstance.get_id(date='20180101', instance_id=0)
    assert sbi_id == 'SBI-20180101-sip-0000'

    sbi_id = SchedulingBlockInstance.get_id(datetime.datetime(2018, 3, 2),
                                            instance_id=12345)
    assert sbi_id == 'SBI-20180302-sip-12345'


def test_sbi_from_config():
    """Test creating an SBI from a configuration dictionary."""
    DB.flush_db()
    sbi_config = generate_sbi_config(num_pbs=2)
    add_test_sbi_workflow_definitions(sbi_config)

    sbi = SchedulingBlockInstance.from_config(sbi_config)
    assert sbi.id == sbi_config['id']
