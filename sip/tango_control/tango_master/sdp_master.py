# -*- coding: utf-8 -*-
"""SKA SDP Master Device prototype."""
import json
import time
import logging
from random import randrange

from config_db import ProcessingBlock, ProcessingBlockList, SDPState, \
    SchedulingBlockInstanceList, ServiceState, generate_sbi_config, \
    SchedulingBlockInstance
from config_db.config_db_redis import ConfigDb
from tango import Database, DbDevInfo, DebugIt, DevState, Util
from tango import DeviceProxy
from tango.server import Device, DeviceMeta, attribute, command


LOG = logging.getLogger('sip.tango_control.SDPMaster')


class SDPMasterDevice(Device, metaclass=DeviceMeta):
    """SIP SDP Master device."""

    _device_version = '1.0.0'
    MC = 'execution_control:master_controller'
    _targetState = 'UNKNOWN'
    _targetTimeStamp = "Unknown"
    _sdp_state = SDPState()
    _sbi_list = SchedulingBlockInstanceList()
    _pb_list = ProcessingBlockList()
    _service_state = ServiceState('TangoControl', 'SDPMaster', _device_version)
    _start_time = time.time()

    # -------------------------------------------------------------------------
    # General methods
    # -------------------------------------------------------------------------
    def init_device(self):
        """Device constructor."""
        Device.init_device(self)
        self.set_state(DevState.INIT)
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
        self.set_state(DevState.STANDBY)
        # TODO(BM) Work out to set the device state (as opposed to status)
        # self.set_state('STANDBY')

    def always_executed_hook(self):
        """FIXME Add docstring."""
        pass

    def delete_device(self):
        """Device destructor."""
        pass

    # ---------------
    # Commands
    # ---------------

    @command(dtype_in=str)
    @DebugIt()
    def configure(self, value):
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

        # devices = db.get_server_list("PB*").value_string

        # pb_list = self._pb_list.active
        # pb_list = ['PB-{:02d}'.format(ii) for ii in range(5)]
        #
        ConfigDb().flush_db()
        sbi_config = generate_sbi_config(register_workflows=True)
        sbi = SchedulingBlockInstance.from_config(sbi_config)
        pb_list = sbi.processing_block_ids
        print('PB_LIST', pb_list)
        active_pbs = ProcessingBlockList.active
        print('ACTIVE', active_pbs)

        # https://pytango.readthedocs.io/en/stable/howto.html#dynamic-device-from-a-known-tango-class-name
        # See if this will work if it is moved to a command on the
        # Processing Block Device?
        # from tango import Util
        # # FIXME first need to register the device?
        # tango_db = Database()
        # dev_info = DbDevInfo()
        # # pylint: disable=protected-access
        # dev_info._class = 'ProcessingBlockDevice'
        # dev_info.server = 'processing_controller_ds/1'
        # dev_info.name = 'sip_sdp/pb/test1'
        # tango_db.add_device(dev_info)
        # util = Util.instance()
        # # cb == callback
        # util.create_device('ProcessingBlockDevice', 'sip_sdp/pb/test1')

        # Get a PB device which has not been assigned.
        for pb in pb_list:
            for ii in range(100):
                pb_dev = 'sip_sdp/pb/PB-{:03d}'.format(ii)
                device = DeviceProxy(pb_dev)
                if not device.pb_id:
                    LOG.info('Assigning PB device = %s to PB id = %s',
                             device.name(), pb)
                    device.pb_id = pb
                    break

        # # https://pytango.readthedocs.io/en/stable/howto.html#dynamic-device-from-a-known-tango-class-name
        # tango_db = Database()
        # for pb in pb_list:
        #     device_name = 'sip_sdp/pb/{}'.format(pb)
        #     device_info = DbDevInfo()
        #     # pylint: disable=protected-access
        #     device_info._class = "ProcessingBlockDevice"
        #     device_info.server = "processing_controller_ds/1"
        #     device_info.name = device_name
        #     tango_db.add_device(device_info)
        #     # util = Util.instance()
        #     # util.create_device('ProcessingBlockDevice', device_name,
        #     #                    alias=None, cb=None)
        #     print('CREATING DEVICE', device_name)
        # print(pb_list)
        # self.debug_stream(pb_list)
        # pb = ProcessingBlock(pb_list[0])
        # print(pb.id)
        return 'added SBI to db!'

    # ------------------
    # Attributes methods
    # ------------------

    @attribute(dtype=str)
    def version(self):
        """Return the version of the Master Controller Device."""
        return self._device_version

    @attribute(dtype=str)
    def current_state(self):
        """Return the current state of the SDP."""
        return self._sdp_state.current_state

    @attribute(label="Target", dtype=str)
    def target_state(self):
        """Return the target state of SDP."""
        # TODO(BMo) add exception handling if the database goes down.
        target_state = self._sdp_state.target_state
        target_timestamp = self._sdp_state.target_timestamp
        self.debug_stream('Fetched target state. value = {}, timestamp = {}'
                          .format(target_state, target_timestamp.isoformat()))
        return target_state

    @target_state.write
    def target_state(self, new_state):
        """Update the target state of SDP."""
        self._sdp_state.update_target_state(new_state)

    @attribute(dtype=float)
    @DebugIt()
    def health_check(self):
        """Health check method, returns the up-time of the device."""
        return time.time() - self._start_time

    # pylint: disable=no-self-use
    @attribute(dtype=str)
    def resource_availability(self):
        """Return the a JSON dict describing the SDP resource amiability."""
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

    @attribute(dtype=str)
    def processing_block_devices(self):
        """Get list of processing block devices."""
        # https://intranet.cells.es/Members/srubio/howto/HowToPyTango#Getalldevicesofaserveroragivenclass
        tango_db = Database()
        # server name, class name
        devices = tango_db.get_device_name('ProcessingController/pcont',
                                           'ProcessingBlockDevice')
        print(devices.value_string)
