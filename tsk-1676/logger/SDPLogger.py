# -*- coding: utf-8 -*-
#
# This file is part of the SDPLogger project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" 

Top-level logging class for SDP code
"""

__all__ = ["SDPLogger", "main"]

# PyTango imports
import PyTango
from PyTango import DebugIt
from PyTango.server import run
from PyTango.server import Device, DeviceMeta
from PyTango.server import attribute, command
from PyTango.server import class_property, device_property
from PyTango import AttrQuality, AttrWriteType, DispLevel, DevState
from SKADevice import SKADevice
# Additional import
# PROTECTED REGION ID(SDPLogger.additionnal_import) ENABLED START #
# PROTECTED REGION END #    //  SDPLogger.additionnal_import


class SDPLogger(SKADevice):
    """
    Top-level logging class for SDP code
    """
    __metaclass__ = DeviceMeta
    # PROTECTED REGION ID(SDPLogger.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  SDPLogger.class_variable
    # ----------------
    # Class Properties
    # ----------------

    # -----------------
    # Device Properties
    # -----------------

    # ----------
    # Attributes
    # ----------

    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        SKADevice.init_device(self)
        # PROTECTED REGION ID(SDPLogger.init_device) ENABLED START #
        # PROTECTED REGION END #    //  SDPLogger.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(SDPLogger.always_executed_hook) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SDPLogger.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(SDPLogger.delete_device) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SDPLogger.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    # --------
    # Commands
    # --------

    @command(dtype_in=('str',), 
    doc_in="# Tango Manual Appendix 9 gives the format\n        # argin[0] = millisecond Unix timestamp\n        # argin[1] = log level\n        # argin[2] = the source log device name\n        # argin[3] = the log message\n        # argin[4] = Not used - reserved\n        # argin[5] = thread identifier of originating message", 
    )
    @DebugIt()
    def log(self, argin):
        # PROTECTED REGION ID(SDPLogger.log) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SDPLogger.log

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(SDPLogger.main) ENABLED START #
    from PyTango.server import run
    return run((SDPLogger,), args=args, **kwargs)
    # PROTECTED REGION END #    //  SDPLogger.main

if __name__ == '__main__':
    main()
