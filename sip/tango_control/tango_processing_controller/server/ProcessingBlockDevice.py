# -*- coding: utf-8 -*-
"""SKA SDP Master Controller prototype."""
import time
from random import randrange
import json
import jsonschema

import PyTango
from PyTango import DebugIt
from PyTango.server import run
from PyTango.server import Device, DeviceMeta
from PyTango.server import attribute, command
from PyTango import AttrQuality, DispLevel, DevState
from PyTango import AttrWriteType, PipeWriteType
from tango import Database, DbDevInfo
from config_db import SDPState, ServiceState
from config_db import SchedulingBlockInstanceList, ProcessingBlockList
from config_db import SchedulingBlockInstance
from config_db import ProcessingBlock


VERSION = '0.0.1'


class ProcessingBlockDevice(Device, metaclass=DeviceMeta):
    """
    SKA SDP Processing Block Device
    """

    def init_device(self):
        """Device constructor."""

    def always_executed_hook(self):
        pass

    def delete_device(self):
        """Device destructor."""
        pass

    # ---------------
    # Commands
    # ---------------

    # ------------------
    # Attributes methods
    # ------------------

    @attribute(dtype=str)
    def version(self):
        """Return the version of the Processing Block Device."""
        return VERSION

    @attribute(dtype=str)
    def id(self):
        """Return the Processing block ID for this device."""
        return self.get_name()
