# -*- coding: utf-8 -*-
"""SKA SDP Tango Processing Block Device."""
# pylint: disable=no-self-use
from tango import DevState
from tango.server import Device, DeviceMeta
from tango.server import attribute

from config_db import ProcessingBlock


VERSION = '0.0.1'


class ProcessingBlockDevice(Device, metaclass=DeviceMeta):
    """Tango Processing Block Device."""

    def init_device(self):
        """Device constructor."""
        self.set_state(DevState.STANDBY)
        self._pb_id = ''

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
    def pb_id(self):
        """Return the Processing block ID for this device."""
        return self._pb_id

    @pb_id.write
    def pb_id(self, pb_id: str):
        """Set the PB Id for this device."""
        # FIXME(BMo) instead of creating the object to check if the PB exists
        #            use a method on PB List?
        ProcessingBlock(pb_id)
        self.set_state(DevState.ON)
        self._pb_id = pb_id

