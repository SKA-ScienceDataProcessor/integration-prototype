# -*- coding: utf-8 -*-
"""Tango Logger device class."""

import time
import datetime

from tango import DebugIt
from tango.server import Device, attribute, class_property, command
from release import LOG, __version__


class SDPLoggerDevice(Device):
    """SDP Logger device class."""

    _start_time = time.time()

    # -------------------------------------------------------------------------
    # General methods
    # -------------------------------------------------------------------------

    def init_device(self):
        """Initialise the device."""
        Device.init_device(self)

    SDP_Devices = ["sip_sdp/elt/master", ]  # (ToDo(BMc) - all DSs)
    #
    #   for dev in SDP_Devices:
    #      d = DeviceProxy(dev)
    #      d.add_logging_target("device::sip_sdp/elt/logger")
    #      LOG.debug("%s device logging targets %s", dev,
    #                 d.get_logging_targets())

    # version = class_property(dtype=str, default_value='test')

    # ---------------
    # Commands
    # ---------------

    @command(dtype_in=(str,), dtype_out=None)
    @DebugIt()
    def log(self, argin):
        """Log a command for the SDP STango ubsystem devices."""
        #
        # Tango Manual Appendix 9 gives the format
        # argin[0] = millisecond Unix timestamp
        # argin[1] = log level
        # argin[2] = the source log device name
        # argin[3] = the log message
        # argin[4] = Not used - reserved
        # argin[5] = thread identifier of originating message

        tm = datetime.datetime.fromtimestamp(float(argin[0])/1000.)
        fmt = "%Y-%m-%d %H:%M:%S"
        message = "TANGO Log message - {} - {} {} {}".format(
            tm.strftime(fmt), argin[1], argin[2], argin[3])
        LOG.info(message)

    # ------------------
    # Attributes methods
    # ------------------

    @attribute(dtype=str)
    def version(self):
        """Return the version of the Master Controller Device."""
        return __version__
