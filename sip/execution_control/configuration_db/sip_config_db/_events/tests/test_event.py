# coding=utf-8
"""Unit tests of the _events.Event class."""

from .. event import Event


def test_create():
    """Test creating an event object."""
    event = Event(event_id='0000', event_type='')
    assert event.id == '0000'
    assert event.type == ''
