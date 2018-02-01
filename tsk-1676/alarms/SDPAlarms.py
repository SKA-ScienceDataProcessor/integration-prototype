# -*- coding: utf-8 -*-
#
# This file is part of the SDPAlarms project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" SDP Alarms Handler

SDP Central Alarms handler
"""

__all__ = ["SDPAlarms", "main"]

# PyTango imports
import PyTango
from PyTango import DebugIt
from PyTango.server import run
from PyTango.server import Device, DeviceMeta
from PyTango.server import attribute, command, pipe
from PyTango.server import class_property, device_property
from PyTango import AttrQuality,DispLevel, DevState
from PyTango import AttrWriteType, PipeWriteType
from SKADevice import SKADevice
# Additional import
# PROTECTED REGION ID(SDPAlarms.additionnal_import) ENABLED START #
# PROTECTED REGION END #    //  SDPAlarms.additionnal_import


class SDPAlarms(SKADevice):
    """
    SDP Central Alarms handler
    """
    __metaclass__ = DeviceMeta
    # PROTECTED REGION ID(SDPAlarms.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  SDPAlarms.class_variable
    # ----------------
    # Class Properties
    # ----------------

    # -----------------
    # Device Properties
    # -----------------

    # ----------
    # Attributes
    # ----------

    # -----
    # Pipes
    # -----

    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        SKADevice.init_device(self)
        # PROTECTED REGION ID(SDPAlarms.init_device) ENABLED START #
        # PROTECTED REGION END #    //  SDPAlarms.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(SDPAlarms.always_executed_hook) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SDPAlarms.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(SDPAlarms.delete_device) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SDPAlarms.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    # -------------
    # Pipes methods
    # -------------

    # --------
    # Commands
    # --------

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(SDPAlarms.main) ENABLED START #
    from PyTango.server import run
    return run((SDPAlarms,), args=args, **kwargs)
    # PROTECTED REGION END #    //  SDPAlarms.main

if __name__ == '__main__':
    main()
