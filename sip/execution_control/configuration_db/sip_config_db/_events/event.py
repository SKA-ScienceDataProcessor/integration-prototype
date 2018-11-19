# coding=utf-8
"""SIP EC config_db event class."""
import datetime


class Event:
    """Event class."""

    def __init__(self, event_id: str, event_type: str, event_data: dict = None,
                 event_origin: str = None,
                 event_timestamp: datetime.datetime = None,
                 object_type: str = None, object_id: str = None,
                 object_key: str = None):
        """Create an Event object.

        Args:
            event_id (str): Event Identifier
            event_type (str): Type of event
            event_data (dict, optional): Event data
            event_origin (str, optional): Event origin
            event_timestamp (datetime.datetime, optional): Created time
            object_type (str, optional): Object type associated with the event
            object_id (str, optional): Object Id associated with the event
            object_key (str, optional): Object key,

        """
        if event_timestamp is None:
            event_timestamp = datetime.datetime.utcnow().isoformat()
        self._event = dict(
            id=event_id,
            type=event_type,
            data=event_data,
            origin=event_origin,
            timestamp=event_timestamp,
            object_type=object_type,
            object_id=object_id,
            object_key=object_key
        )

    @classmethod
    def from_config(cls, config: dict):
        """Create an event object from an event dictionary object.

        {
            'id': "",
            'type': "",
            'data': {},
            'origin': "",
            'timestamp': "",
            'object_id': "",
            'object_type': ""
        }
        """
        timestamp = config.get('timestamp', None)
        # if timestamp:
        #     timestamp = datetime_from_isoformat(timestamp)
        return cls(config.get('id'),
                   config.get('type'),
                   config.get('data', dict()),
                   config.get('origin', None),
                   timestamp,
                   config.get('object_type', None),
                   config.get('object_id', None),
                   config.get('object_key', None))

    def __str__(self):
        """Generate the 'informal' string representation.

        Used by the print statement.
        """
        return str(self._event)

    def __repr__(self):
        """Generate the 'official' string representation.

        eg. used when printing lists of objects.
        """
        return '{}'.format(self._event.get('id'))

    @property
    def config(self) -> dict:
        """Event configuration dictionary."""
        return self._event

    # pylint: disable=invalid-name
    @property
    def id(self) -> str:
        """Return the event id."""
        return self._event.get('id')

    @property
    def type(self) -> str:
        """Return the type of event."""
        return self._event.get('type')

    @property
    def data(self) -> dict:
        """Return the event data."""
        return self._event.get('data')

    @property
    def origin(self) -> str:
        """Return the event data."""
        return self._event.get('origin')

    @property
    def timestamp(self) -> str:
        """Return the event data."""
        return self._event.get('timestamp')

    @property
    def object_type(self) -> str:
        """Return the object type associated with the event."""
        return self._event.get('object_type')

    @property
    def object_id(self) -> str:
        """Return the object id associated with the event."""
        return self._event.get('object_id')

    @property
    def object_key(self) -> str:
        """Return the object key associated with the event."""
        return self._event.get('object_key')
