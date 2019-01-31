# -*- coding: utf-8 -*-
"""Tango Logger device class."""

import json
import time

import jsonschema
import datetime

from tango import DebugIt, DevState, DeviceProxy

from tango.server import Device, attribute, class_property, command, pipe
from release import LOG, __service_name__, __subsystem__, __version__

class SDPLoggerDevice(Device):
    """SDP Logger device class."""

    _start_time = time.time()

    # -------------------------------------------------------------------------
    # General methods
    # -------------------------------------------------------------------------

    def init_device(self):
        """Initialise the device."""
        Device.init_device(self)

        SDP_Devices = ["sdp/elt/master", ] # Plus ALL PDB and Subarray devices!!!

        for dev in SDP_Devices:
            d = DeviceProxy(dev)
            d.add_logging_target("device::sdp/elt/logger")
            LOG.info("Logging targets %s", d.get_logging_targets())

    # version = class_property(dtype=str, default_value='test')

    # ---------------
    # Commands
    # ---------------
    @command(dtype_in=(str,), dtype_out=None)
    @DebugIt()
    def log(self, argin):
        """Log a command for the SDP STango ubsystem devices."""
      # Tango Manual Appendix 9 gives the format
        # argin[0] = millisecond Unix timestamp
        # argin[1] = log level
        # argin[2] = the source log device name
        # argin[3] = the log message
        # argin[4] = Not used - reserved
        # argin[5] = thread identifier of originating message

        t = datetime.datetime.fromtimestamp(float(argin[0])/1000.)
        fmt = "%Y-%m-%d %H:%M:%S"
        message = "TANGO Log message - {} - {} {} {}".format(t.strftime(fmt),argin[1],
             argin[2], argin[3])
        LOG.info(message)



   