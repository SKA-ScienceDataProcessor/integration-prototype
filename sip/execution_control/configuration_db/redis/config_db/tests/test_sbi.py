# -*- coding: utf-8 -*-
"""Tests of the Scheduling Block Instance API."""
import datetime
from ..sbi import SchedulingBlockInstance as sbi


def test_get_sbi_id():
    """Test static method to generate a valid SBI id."""
    utc_now = datetime.datetime.utcnow()
    instance_id = 1
    sbi_id = sbi.get_id(utc_now, project='sip', instance_id=instance_id)
    assert sbi_id == 'SBI-{}-sip-{:04d}'.format(utc_now.strftime('%Y%m%d'),
                                                instance_id)
    sbi_id = sbi.get_id(utc_now, project='test', instance_id=0)
    assert sbi_id == 'SBI-{}-test-0000'.format(utc_now.strftime('%Y%m%d'))

    sbi_id = sbi.get_id(date='20180101', instance_id=0)
    assert sbi_id == 'SBI-20180101-sip-0000'

    sbi_id = sbi.get_id(datetime.datetime(2018, 3, 2), instance_id=12345)
    assert sbi_id == 'SBI-20180302-sip-12345'
