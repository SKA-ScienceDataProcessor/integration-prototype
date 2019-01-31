# -*- coding: utf-8 -*-
"""Tests of the Scheduling data object base class."""
import pytest

from .._scheduling_object import SchedulingObject


def test_scheduling_object_init_exceptions():
    """Test creating a scheduling object"""
    with pytest.raises(RuntimeError):
        SchedulingObject('foo', '')

    with pytest.raises(KeyError):
        SchedulingObject('pb', 'pb-01')

    with pytest.raises(KeyError):
        SchedulingObject('sbi', 'sbi-01')
