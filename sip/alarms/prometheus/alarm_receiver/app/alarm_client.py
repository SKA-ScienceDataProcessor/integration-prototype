# -*- coding: utf-8 -*-
"""High Level Master Controller Client API."""
from .config_db_redis import ConfigDb


class AlarmDbClient:
    """Alarm Handler Client Interface."""

    def __init__(self):
        """Initialise the Alarm Hnadler Database client."""
        self._db = ConfigDb()

    ###########################################################################
    # Update functions
    ###########################################################################

    def update_value(self, value):
        """Update the value of the alarm."""
        for key in value:
            self._db.set_hash_value('alarm', key, value[key])
