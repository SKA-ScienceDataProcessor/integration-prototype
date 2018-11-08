# -*- coding: utf-8 -*-
#
# This file is part of the MasterController project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" 

SKA SDP Master Controller prototype
"""

# PyTango imports
import PyTango
from PyTango import DebugIt
from PyTango.server import run
from PyTango.server import Device, DeviceMeta
from PyTango.server import attribute, command
from PyTango import AttrQuality, DispLevel, DevState
from PyTango import AttrWriteType, PipeWriteType
from SKADevice import SKADevice
# Additional import
from master_client import masterClient
import redis

__all__ = ["MasterController", "main"]


class MasterController(SKADevice,metaclass=DeviceMeta):
    """
    SKA SDP Master Controller prototype
    """
    MC = 'execution_control:master_controller'
    _targetState = 'UNKNOWN'
    _targetTimeStamp = "Unknown"

    # ----------
    # Attributes
    # ----------



    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        SKADevice.init_device(self)
        #self.set_status('BUBBLE')

    def always_executed_hook(self):
        pass

    def delete_device(self):
        pass

    # ------------------
    # Attributes methods
    # ------------------

    @attribute(label="Target", dtype=str)
    def targetState(self):
        db = masterClient() 
        try:
           self._targetState = db.get_value(self.MC, "Target_state")
           self._targetTimeStamp = db.get_value(self.MC, "Target_timestamp")
        except:# redis.exceptions.ConnectionError:
            self.debug_stream('failed to connect to DB')

        self.debug_stream("Target_state = {} TimeStamp={}".
                          format(self._targetState, self._targetTimeStamp))
      
        return  self._targetState

    @targetState.write
    def targetState(self, newState):
#        self.debug_stream("In targetState.write")
        newState = newState.upper()
        states = ['OFF', 'STANDBY', 'ON', 'DISABLE']

        if newState not in states:
            PyTango.Except.throw_exception("PyTango.DevFailed",\
                "NOTVALID",\
                newState + " is not a valid target state")

        db = masterClient() 
        try:
            self.debug_stream('updating state')
            db.update_target_state( 'Target_state', newState)
        except redis.exceptions.ConnectionError:
            self.debug_stream('failed to connect to DB')
        self.debug_stream("update complete")

    @attribute(dtype=str)
    @DebugIt()
    def HeartBeat(self):
        mc = masterClient()
        value = mc.get_value('execution_control:master_controller',
                    'State_timestamp')
        return value

    # --------
    # Commands
    # --------

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    return run((MasterController,), args=args, **kwargs)

if __name__ == '__main__':
    main()
