# coding=utf-8
"""Unit tests of the _events.Event class."""


def test_event_create():
    """Test creating an event object."""
    from ..event import Event
    event = Event(event_id='0000',
                  event_type='event_type')
    assert event.id == '0000'
    assert event.type == 'event_type'
