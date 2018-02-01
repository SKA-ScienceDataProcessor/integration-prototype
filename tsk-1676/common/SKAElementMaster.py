# -*- coding: utf-8 -*-
#
# This file is part of the SKAElementMaster project
#
# GPL
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" SKADevice

Base classes according to current state of 
``SKA1 TANGO Developers Guideline - Rev 01``
"""

__all__ = ["SKAElementMaster", "main"]

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
# PROTECTED REGION ID(SKAElementMaster.additionnal_import) ENABLED START #
# PROTECTED REGION END #    //  SKAElementMaster.additionnal_import


class SKAElementMaster(SKADevice):
    """
    Base classes according to current state of 
    ``SKA1 TANGO Developers Guideline - Rev 01``
    """
    __metaclass__ = DeviceMeta
    # PROTECTED REGION ID(SKAElementMaster.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  SKAElementMaster.class_variable
    # ----------------
    # Class Properties
    # ----------------

    # -----------------
    # Device Properties
    # -----------------

    # ----------
    # Attributes
    # ----------

    startupProgress = attribute(
        dtype='int16',
    )
    # -----
    # Pipes
    # -----

    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        SKADevice.init_device(self)
        # PROTECTED REGION ID(SKAElementMaster.init_device) ENABLED START #
        # PROTECTED REGION END #    //  SKAElementMaster.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(SKAElementMaster.always_executed_hook) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SKAElementMaster.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(SKAElementMaster.delete_device) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SKAElementMaster.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_startupProgress(self):
        # PROTECTED REGION ID(SKAElementMaster.startupProgress_read) ENABLED START #
        return 0
        # PROTECTED REGION END #    //  SKAElementMaster.startupProgress_read

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
    # PROTECTED REGION ID(SKAElementMaster.main) ENABLED START #
    from PyTango.server import run
    return run((SKAElementMaster,), args=args, **kwargs)
    # PROTECTED REGION END #    //  SKAElementMaster.main

if __name__ == '__main__':
    main()
