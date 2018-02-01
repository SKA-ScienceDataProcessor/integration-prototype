# -*- coding: utf-8 -*-
#
# This file is part of the SKADevice project
#
# GPL
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" SKA base class for ELT masters

A test base class for use witn Pogo in SDP development - taken from 
SKA1 TANGO Developers Guideline - Rev01

* Likely to be superceded *
"""

__all__ = ["SKADevice", "main"]

# PyTango imports
import PyTango
from PyTango import DebugIt
from PyTango.server import run
from PyTango.server import Device, DeviceMeta
from PyTango.server import attribute, command, pipe
from PyTango.server import class_property, device_property
from PyTango import AttrQuality,DispLevel, DevState
from PyTango import AttrWriteType, PipeWriteType
# Additional import
# PROTECTED REGION ID(SKADevice.additionnal_import) ENABLED START #
# PROTECTED REGION END #    //  SKADevice.additionnal_import


class SKADevice(Device):
    """
    A test base class for use witn Pogo in SDP development - taken from 
    SKA1 TANGO Developers Guideline - Rev01
    
    * Likely to be superceded *
    """
    __metaclass__ = DeviceMeta
    # PROTECTED REGION ID(SKADevice.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  SKADevice.class_variable
    # ----------------
    # Class Properties
    # ----------------

    # -----------------
    # Device Properties
    # -----------------

    # ----------
    # Attributes
    # ----------

    healthState = attribute(
        dtype='DevEnum',
        doc="IIndicates the overall rolled up health status of the Element as interpreted by \nthe ElementMaster",
        enum_labels=["OK", "DEGRADED", "FAILED", "UNKNOWN", ],
    )
    adminMode = attribute(
        dtype='DevEnum',
        enum_labels=["ONLINE", "OFFLINE", "MAINTENANCE", "NOT-FITTED", "RESERVED", ],
    )
    obsState = attribute(
        dtype='DevEnum',
        enum_labels=["IDLE", "CONFIGURING", "READY", "SCANNING", "PAUSED", "ABORTED", "FAULT", ],
    )
    simulationMode = attribute(
        dtype='bool',
    )
    testMode = attribute(
        dtype='DevEnum',
        enum_labels=["NONE", "custom-values", ],
    )
    controlMode = attribute(
        dtype='DevEnum',
        enum_labels=["UNRESTRICTED", "CENTRAL", "LOCAL", ],
    )
    configurationProgress = attribute(
        dtype='int16',
        doc="Optional. Is required if obsState is implemented\nProvides a progress report on Scan Configuration progress with a % indication. \n100 indicates completion\n",
    )
    SkaLevel = attribute(
        dtype='char',
        doc="Indication of importance of the device in the SKA hierarchy to support drill-down navigation: \n1..6, with 1 highest\n",
    )
    versionId = attribute(
        dtype='str',
        doc="Version ID for this Element to TM interface. \nThis has to be unique and is indicative of a different SDD.\nA string in the format XX.YY to indicate the Element interface version where XX indicates \nthe major version and YY indicates the minor version.\nEach of the Element Level device servers will have a 'versionId' attribute to accurately \nidentify different versions of the Element to TM interface.\n",
    )
    buildState = attribute(
        dtype='str',
        doc="Build state of this device",
    )
    # -----
    # Pipes
    # -----

    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        Device.init_device(self)
        # PROTECTED REGION ID(SKADevice.init_device) ENABLED START #
        # PROTECTED REGION END #    //  SKADevice.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(SKADevice.always_executed_hook) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SKADevice.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(SKADevice.delete_device) ENABLED START #
        pass
        # PROTECTED REGION END #    //  SKADevice.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_healthState(self):
        # PROTECTED REGION ID(SKADevice.healthState_read) ENABLED START #
        return 
        # PROTECTED REGION END #    //  SKADevice.healthState_read

    def read_adminMode(self):
        # PROTECTED REGION ID(SKADevice.adminMode_read) ENABLED START #
        return 
        # PROTECTED REGION END #    //  SKADevice.adminMode_read

    def read_obsState(self):
        # PROTECTED REGION ID(SKADevice.obsState_read) ENABLED START #
        return 
        # PROTECTED REGION END #    //  SKADevice.obsState_read

    def read_simulationMode(self):
        # PROTECTED REGION ID(SKADevice.simulationMode_read) ENABLED START #
        return False
        # PROTECTED REGION END #    //  SKADevice.simulationMode_read

    def read_testMode(self):
        # PROTECTED REGION ID(SKADevice.testMode_read) ENABLED START #
        return 
        # PROTECTED REGION END #    //  SKADevice.testMode_read

    def read_controlMode(self):
        # PROTECTED REGION ID(SKADevice.controlMode_read) ENABLED START #
        return 
        # PROTECTED REGION END #    //  SKADevice.controlMode_read

    def read_configurationProgress(self):
        # PROTECTED REGION ID(SKADevice.configurationProgress_read) ENABLED START #
        return 0
        # PROTECTED REGION END #    //  SKADevice.configurationProgress_read

    def read_SkaLevel(self):
        # PROTECTED REGION ID(SKADevice.SkaLevel_read) ENABLED START #
        return 0
        # PROTECTED REGION END #    //  SKADevice.SkaLevel_read

    def read_versionId(self):
        # PROTECTED REGION ID(SKADevice.versionId_read) ENABLED START #
        return ''
        # PROTECTED REGION END #    //  SKADevice.versionId_read

    def read_buildState(self):
        # PROTECTED REGION ID(SKADevice.buildState_read) ENABLED START #
        return ''
        # PROTECTED REGION END #    //  SKADevice.buildState_read

    # -------------
    # Pipes methods
    # -------------

    # --------
    # Commands
    # --------

    @command(
    dtype_out=('str',), 
    )
    @DebugIt()
    def GetVersionInfo(self):
        # PROTECTED REGION ID(SKADevice.GetVersionInfo) ENABLED START #
        return [""]
        # PROTECTED REGION END #    //  SKADevice.GetVersionInfo

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(SKADevice.main) ENABLED START #
    from PyTango.server import run
    return run((SKADevice,), args=args, **kwargs)
    # PROTECTED REGION END #    //  SKADevice.main

if __name__ == '__main__':
    main()
