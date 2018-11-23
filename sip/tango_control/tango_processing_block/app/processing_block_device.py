# -*- coding: utf-8 -*-
"""SKA SDP Tango Processing Block Device."""
# pylint: disable=no-self-use,attribute-defined-outside-init
import time
import json
from tango import DevState
from tango.server import Device, attribute

from release import LOG, __version__ as tango_pb_device_version
from sip_config_db.scheduling import ProcessingBlock


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
        return tango_pb_device_version

    @attribute(dtype=str)
    def pb_id(self):
        """Return the Processing block ID for this device."""
        return self._pb_id

    @pb_id.write
    def pb_id(self, pb_id: str):
        """Set the PB Id for this device."""
        # FIXME(BMo) instead of creating the object to check if the PB exists
        #            use a method on PB List?
        # ProcessingBlock(pb_id)
        self.set_state(DevState.ON)
        self._pb_id = pb_id

    @attribute(dtype=str)
    def pb_config(self):
        """Return the PB configuration."""
        pb = ProcessingBlock(self._pb_id)
        return json.dumps(pb.config)

    @attribute(dtype=str)
    def pb_status(self):
        """Return the PB status."""
        pb = ProcessingBlock(self._pb_id)
        return pb.status

    @attribute(dtype=str)
    def pb_type(self):
        """Return the PB type."""
        pb = ProcessingBlock(self._pb_id)
        return pb.type

    @attribute(dtype=str)
    def sbi_id(self):
        """Return the PB SBI ID."""
        pb = ProcessingBlock(self._pb_id)
        return pb.sbi_id

    @attribute(dtype=str)
    def pb_version(self):
        """Return the PB version."""
        pb = ProcessingBlock(self._pb_id)
        return pb.version

    @attribute(dtype=str)
    def pb_last_updated(self):
        """Return the PB ."""
        pb = ProcessingBlock(self._pb_id)
        return pb.updated.isoformat()

    @attribute(dtype=str)
    def pb_created(self):
        """Return the PB ."""
        pb = ProcessingBlock(self._pb_id)
        return pb.created.isoformat()
