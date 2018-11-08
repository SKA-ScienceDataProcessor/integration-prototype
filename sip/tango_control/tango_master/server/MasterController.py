# -*- coding: utf-8 -*-
"""SKA SDP Master Controller prototype."""
import time
from random import randrange
import json
import jsonschema

import PyTango
from PyTango import DebugIt
from PyTango.server import run
from PyTango.server import Device, DeviceMeta
from PyTango.server import attribute, command
from PyTango import AttrQuality, DispLevel, DevState
from PyTango import AttrWriteType, PipeWriteType
from SKADevice import SKADevice
from tango import Database, DbDevInfo
from config_db import SDPState, ServiceState
from config_db import SchedulingBlockInstanceList, ProcessingBlockList
from config_db import SchedulingBlockInstance
from config_db import ProcessingBlock


__all__ = ["MasterController", "main"]
VERSION = 'test'


class MasterController(SKADevice, metaclass=DeviceMeta):
    """
    SKA SDP Master Controller prototype
    """
    MC = 'execution_control:master_controller'
    _targetState = 'UNKNOWN'
    _targetTimeStamp = "Unknown"
    _sdp_state = SDPState()
    _sbi_list = SchedulingBlockInstanceList()
    _pb_list = ProcessingBlockList()
    _service_state = ServiceState('TangoControl', 'SDPMaster', VERSION)

    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        """Device constructor."""
        SKADevice.init_device(self)
        self._start_time = time.time()
        self.set_status('INIT')
        # TODO(BMo) Check if the current state of all services are 'on'
        # TODO(BMo) add methods on database for ServiceList to be able to
        # iterate over sdp services to be able to call the current state
        # property on each
        # For now this is mocked by this sleep
        time.sleep(0.1)
        # FIXME(BMo) Fix the state logic so that we dont have to check the
        # current state when reinitialising device.
        if self._service_state.current_state == 'unknown':
            self._service_state.update_current_state('init')
        if self._sdp_state.current_state == 'unknown':
            self._sdp_state.update_current_state('init')

        if self._sdp_state.current_state == 'standby':
            self._sdp_state.update_current_state('standby')
        if self._service_state.current_state != 'on':
            self._service_state.update_current_state('on')
        self.set_status('STANDBY')
        # TODO(BM) Work out to set the device state (as opposed to status)
        # self.set_state('STANDBY')

    def always_executed_hook(self):
        pass

    def delete_device(self):
        """Device destructor."""
        pass

    # ---------------
    # Commands
    # ---------------

    @command(dtype_in=str)
    @DebugIt()
    def configure(self, sbi_config):
        """Schedule an offline only SBI with SDP."""
        # FIXME(BMo) something in from_config is not respecting REDIS_HOST!
        # config_dict = json.loads(sbi_config)
        # sbi = SchedulingBlockInstance.from_config(config_dict)
        # try:
        #
        # except jsonschema.exceptions.ValidationError as error:
        #     raise
        #     # return 'failed to parse json'
        # return 'added SBI with ID = {}'.format(sbi.id)

        # sdp/pb/PB - xxxxxx
        db = Database()
        # devices = db.get_server_list("PB*").value_string

        pb_list = self._pb_list.active

        for pb in pb_list:
            device_name = 'sdp/ProcessingBlock/{}'.format(pb)
            new_device_info = DbDevInfo()
            new_device_info._class = "ProcessingBlockDevice"
            new_device_info.server = "ProcessingControllerDS/test"
            new_device_info.name = device_name
            db.add_device(new_device_info)
            print('CREATING DEVICE', device_name)
        print(pb_list)
        # self.debug_stream(pb_list)
        pb = ProcessingBlock(pb_list[0])
        print(pb.id)
        return 'added SBI to db!'

    # ------------------
    # Attributes methods
    # ------------------

    @attribute(dtype=str)
    def version(self):
        """Return the version of the Master Controller Device."""
        return VERSION

    @attribute(dtype=str)
    def current_state(self):
        """Return the current state of the SDP."""
        return self._sdp_state.current_state

    @attribute(label="Target", dtype=str)
    def target_state(self):
        """Return the target state of SDP."""
        # TODO(BMo) add exception handling if the database goes down.
        self.debug_stream('Fetched target state. value = {}, timestamp = {}'
                          .format(self._sdp_state.target_state,
                                  self._sdp_state.target_timestamp.isoformat()))
        return self._sdp_state.target_state

    @target_state.write
    def target_state(self, new_state):
        """Update the target state of SDP."""
        self._sdp_state.update_target_state(new_state)

    @attribute(dtype=float)
    @DebugIt()
    def health_check(self):
        """Health check method, returns the up-time of the device."""
        return time.time() - self._start_time

    @attribute(dtype=str)
    def resource_availability(self):
        """Return the a JSON dict describing the SDP resource amiability. """
        # TODO(BMo) change this to a pipe?
        return json.dumps(dict(nodes_free=randrange(0, 500)))

    @attribute(dtype=str)
    def scheduling_block_instances(self):
        """Return the a JSON dict encoding the SBIs known to SDP."""
        # TODO(BMo) change this to a pipe?
        active_sbis = self._sbi_list.active
        return json.dumps(dict(sbi_list=active_sbis))

    @attribute(dtype=str)
    def processing_blocks(self):
        """Return the a JSON dict encoding the PBs known to SDP."""
        # TODO(BMo) change this to a pipe?
        active_pbs = self._pb_list.active
        return json.dumps(dict(pb_list=active_pbs))

    @attribute(dtype=str)
    def offline_processing_blocks(self):
        """Return the a JSON dict encoding the offline PBs known to SDP."""
        # TODO(BMo) change this to a pipe?
        # TODO(BMo) add property to ProcessingBlockList to get offline \
        # processing

    @attribute(dtype=str)
    def realtime_processing_blocks(self):
        """Return the a JSON dict encoding the realtime SBIs known to SDP."""
        # TODO(BMo) change this to a pipe?
        # TODO(BMo) add property to ProcessingBlockList to get realtime \
        # processing


# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    return run((MasterController,), args=args, **kwargs)


if __name__ == '__main__':
    main()
