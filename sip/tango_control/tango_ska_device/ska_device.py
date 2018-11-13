# -*- coding: utf-8 -*-
"""Experimental SKA base class for ELT devices.

A test base class for use with Pogo in SIP prototyping - taken from
SKA1 TANGO Developers Guideline - Rev01

* Likely to be superseded *
"""
# pylint: disable-all
from tango import DebugIt
from tango.server import Device, DeviceMeta, attribute, command


class SKADevice(Device):
    """
    A test base class for use with Pogo in SDP development - taken from
    SKA1 TANGO Developers Guideline - Rev01

    * Likely to be superseded *
    """
    __metaclass__ = DeviceMeta

    # ----------
    # Attributes
    # ----------

    healthState = attribute(
        dtype='DevEnum',
        doc="Indicates the overall rolled up health status of the "
            "Element as interpreted by \nthe ElementMaster",
        enum_labels=["OK", "DEGRADED", "FAILED", "UNKNOWN", ],
    )

    adminMode = attribute(
        dtype='DevEnum',
        enum_labels=["ONLINE", "OFFLINE", "MAINTENANCE", "NOT-FITTED",
                     "RESERVED", ],
    )

    obsState = attribute(
        dtype='DevEnum',
        enum_labels=["IDLE", "CONFIGURING", "READY", "SCANNING",
                     "PAUSED", "ABORTED", "FAULT", ],
    )

    simulationMode = attribute(dtype='bool',)

    testMode = attribute(dtype='DevEnum',
                         enum_labels=["NONE", "custom-values", ],)

    controlMode = attribute(
        dtype='DevEnum',
        enum_labels=["UNRESTRICTED", "CENTRAL", "LOCAL", ],
    )

    configurationProgress = attribute(
        dtype='int16',
        doc="Optional. Is required if obsState is implemented\n"
            "Provides a progress report on Scan Configuration progress "
            "with a % indication. \n100 indicates completion\n",
    )

    SkaLevel = attribute(
        dtype='char',
        doc="Indication of importance of the device in the SKA hierarchy "
            "to support drill-down navigation: \n1..6, with 1 highest\n",
    )

    versionId = attribute(
        dtype='str',
        doc="Version ID for this Element to TM interface. \nThis has to be "
            "unique and is indicative of a different SDD.\nA string in the "
            "format XX.YY to indicate the Element interface version where "
            "XX indicates \nthe major version and YY indicates the minor "
            "version.\nEach of the Element Level device servers will have "
            "a 'versionId' attribute to accurately \nidentify different "
            "versions of the Element to TM interface.\n",
    )

    buildState = attribute(
        dtype='str',
        doc="Build state of this device",
    )

    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        Device.init_device(self)

    def always_executed_hook(self):
        pass

    def delete_device(self):
        pass

    # ------------------
    # Attributes methods
    # ------------------

    def read_healthState(self):
        return ''

    def read_adminMode(self):
        return ''

    def read_obsState(self):
        return ''

    def read_simulationMode(self):
        return False

    def read_testMode(self):
        return ''

    def read_controlMode(self):
        return ''

    def read_configurationProgress(self):
        return 0

    def read_SkaLevel(self):
        return 0

    def read_versionId(self):
        return ""

    def read_buildState(self):
        return ""

    # --------
    # Commands
    # --------

    @command(dtype_out=('str',),)
    @DebugIt()
    def GetVersionInfo(self):
        return [""]

    @command(dtype_in='str',)
    @DebugIt()
    def SetTargetState(self, argin):
        pass
