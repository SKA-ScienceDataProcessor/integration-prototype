# -*- coding: utf-8 -*-
"""High-level interface for a list of Processing Block (PB) objects."""
from ._keys import PB_KEY
from ._scheduling_object_list import SchedulingObjectList


class ProcessingBlockList(SchedulingObjectList):
    """Configuration Database Processing Block List API."""

    def __init__(self):
        """Initialise variables."""
        SchedulingObjectList.__init__(self, PB_KEY)
