# -*- coding: utf-8 -*-
"""Tests of the low level Redis client API.

For instructions of how to run these tests see the README.md file in the
`sip/configuration_db/redis` folder.

Todo:
    - Unit tests handling invalid types eg. asking for the length of a list
      when the type is a hash.
"""
import ast

import pytest

from ..config_db_redis import ConfigDbRedis


def test_get_client_object():
    """Test creating a database client object."""
    db_client = ConfigDbRedis()
    assert db_client is not None
    try:
        db_client.flush_db()
    except ConnectionError:
        pytest.fail("Failed to connect to Redis database.")


def test_hash_methods():
    """Test methods for handling values stored in a Redis hash type.

    This is used extensively as a way of storing hierarchical structures in the
    configuration database.
    """
    db_client = ConfigDbRedis()
    try:
        db_client.flush_db()
    except ConnectionError:
        pytest.fail("Failed to connect to Redis database.")

    # Test setting and getting multiple values in a Redis Hash.
    db_client.set_hash_values(key="hash", fields=dict(key1="foo", key2="bar"))
    values = db_client.get_hash_values(key="hash", fields=['key1', 'key2'])
    assert values == ['foo', 'bar']

    values = db_client.get_hash_values(key="hash", fields=['key2', 'key1'])
    assert values == ['bar', 'foo']

    # Test setting and getting single values in a Redis Hash.
    db_client.set_hash_value(key="hash", field="key3", value=2)
    # NOTE(BM) hash values are stored and returned as strings!
    assert db_client.get_hash_value(key='hash', field='key3') == '2'

    values = db_client.get_hash_dict(key="hash")
    assert len(values) == 3
    assert 'key1' in values
    assert 'key2' in values
    assert 'key3' in values
    assert values['key1'] == 'foo'
    assert values['key2'] == 'bar'
    assert values['key3'] == '2'


def test_set_get_list():
    """Test methods for handling values stored in lists."""
    db_client = ConfigDbRedis()
    try:
        db_client.flush_db()
    except ConnectionError:
        pytest.fail("Failed to connect to Redis database.")

    db_client.append_to_list(key="my_list", value=0)
    db_client.append_to_list(key="my_list", value=1)
    db_client.append_to_list(key="my_list", value=2)
    db_client.prepend_to_list(key="my_list", value='a')

    # NOTE(BM) values are returned as strings!
    assert db_client.get_list_value('my_list', 0) == 'a'
    assert db_client.get_list_value('my_list', 1) == '0'
    assert db_client.get_list_value('my_list', 2) == '1'
    assert db_client.get_list_value('my_list', 3) == '2'

    values = db_client.get_list('my_list')
    assert values == ['a', '0', '1', '2']

    assert db_client.get_list_length('my_list') == 4

    # Delete the list and check that it is gone.
    db_client.delete_key('my_list')
    assert not db_client.key_exists('my_list')

    # Asking for a list that doesnt exist returns a list with no entries.
    # NOTE(BM) Not sure this is ideal behaviour - needs review.
    values = db_client.get_list('my_list')
    assert not values


def test_events():
    """Test methods for handling events stored in the database.

    NOTE(BM):
        These functions need some work or moving to a higher level in the
        client library.
    """
    db_client = ConfigDbRedis()
    try:
        db_client.flush_db()
    except ConnectionError:
        pytest.fail("Failed to connect to Redis database.")

    db_client.push_event(event_name='my_event', event_type='type',
                         block_id='id')
    event = db_client.get_event(event_name='my_event')
    # Events are currently returned in a string representation.
    # This is probably not ideal and needs some thought.
    assert isinstance(event, str)

    # In normal use, the event is converted back to an object.
    event = ast.literal_eval(event)
    assert event['type'] == 'type'
    assert event['id'] == 'id'
