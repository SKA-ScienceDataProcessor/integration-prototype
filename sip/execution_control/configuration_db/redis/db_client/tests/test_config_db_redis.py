# -*- coding: utf-8 -*-
r"""Tests of the low level Redis client API.

Run with:

    py.test --pylint --codestyle -s -v --durations=3 \
        --pylint-rcfile=../../../../.pylintrc \
        db_client/tests/test_config_db_redis.py
"""
from ..config_db_redis import ConfigDbRedis


def test_get_client_object():
    """Test creating a database client object."""
    db_client = ConfigDbRedis()
    assert db_client is not None


def test_set_values():
    """Test setting some values."""
    db_client = ConfigDbRedis()
    db_client.set_specified_values("foo", "bar")
