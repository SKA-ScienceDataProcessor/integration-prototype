# -*- coding: utf-8 -*-
#
# This file is part of the SDPTelModel project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" SDP Telescope Model

Placeholder to be developed into the SDP Telscope Model class
"""

__all__ = ["SDPTelModel", "main"]

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
# PROTECTED REGION ID(SDPTelModel.additionnal_import) ENABLED START #
# PROTECTED REGION END #    //  SDPTelModel.additionnal_import


class SDPTelModel(SKADevice):
    """
    Placeholder to be developed into the SDP Telscope Model class
    """
    __metaclass__ = DeviceMeta
    # PROTECTED REGION ID(SDPTelModel.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  SDPTelModel.class_variable
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
        # PROTECTED REGION ID(SDPTelModel.init_device) ENABLED START #
        # PROTECTED REGION END #    //  SDPTelModel.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(SDPTelModel.always_executed_hook) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SDPTelModel.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(SDPTelModel.delete_device) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SDPTelModel.delete_device

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
    # PROTECTED REGION ID(SDPTelModel.main) ENABLED START #
    from PyTango.server import run
    return run((SDPTelModel,), args=args, **kwargs)
    # PROTECTED REGION END #    //  SDPTelModel.main

if __name__ == '__main__':
    main()
