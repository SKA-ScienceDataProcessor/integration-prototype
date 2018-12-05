# coding=utf-8
"""Tests of the low level Redis DB API."""
import pytest
from .. import ConfigDb

DB = ConfigDb()

# TODO(BMo) Test fixture to reset and cleanup the database


def test_config_db_version():
    """Make sure we are using the version we expect!"""
    from .. import __version__
    import redis
    assert __version__ == '1.2.1'
    assert redis.__version__ == '2.10.6'


@pytest.mark.parametrize('hierarchical', [True, False])
def test_config_db_redis_store_dict(hierarchical: bool):
    """Test setting hash values into the database."""
    DB.flush_db()
    test_dict = dict(a=1, b=dict(c='1.0.0', d=dict(foo=1, bar='hello')))
    key = 'test_dict_1'
    DB.save_dict(key, test_dict, hierarchical=hierarchical)
    my_dict = DB.load_dict(key, hierarchical=hierarchical)
    assert test_dict == my_dict
    test_dict = dict(a=1, b=['l1', 'l2', 'l3'])
    key = 'test_dict_2'
    DB.save_dict(key, test_dict, hierarchical=hierarchical)
    my_dict = DB.load_dict(key, hierarchical=hierarchical)
    assert test_dict == my_dict


@pytest.mark.parametrize('hierarchical', [True, False])
def test_config_db_redis_load_dict_values(hierarchical: bool):
    """Test setting hash values into the database."""
    DB.flush_db()
    test_dict = dict(a=1, b=dict(c=3))
    key = 'test_dict'
    DB.save_dict(key, test_dict, hierarchical=hierarchical)
    load_fields = ['a', 'b']
    values = DB.load_dict_values(key, load_fields, hierarchical=hierarchical)
    test_values = [test_dict[v] for v in load_fields]
    assert len(values) == len(test_values)
    for item in values:
        assert item in test_values
