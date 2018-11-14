# -*- coding: utf-8 -*-
"""SKA SDP Tango Processing Block Device."""
import time
import logging

# pylint: disable=no-self-use
from tango import DevState, Database, DbDevInfo
from tango.server import Device, DeviceMeta
from tango.server import attribute, command

from config_db import ProcessingBlock


VERSION = '0.0.1'
LOG = logging.getLogger('sip.tango_control.pb_device')


class ProcessingBlockDevice(Device):
    """Tango Processing Block Device."""

    _start_time = time.time()

    def init_device(self):
        """Device constructor."""
        start_time = time.time()
        Device.init_device(self)
        self._pb_id = ''
        LOG.debug('init PB device %s, time taken %.6f s (total: %.2f s)',
                  self.get_name(), (time.time() - start_time),
                  (time.time() - self._start_time))
        self.set_state(DevState.STANDBY)

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

