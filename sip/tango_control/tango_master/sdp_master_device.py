# -*- coding: utf-8 -*-
"""SKA SDP Master Device prototype.

TODO(BMo): Exception handling if the config database is dead.

"""
# pylint: disable=no-self-use
import json
import logging
import time
from random import randrange

from tango import Database, DebugIt, DevState, DeviceProxy
from tango.server import Device, attribute, command

from config_db import ProcessingBlockList, SDPState, SchedulingBlockInstance, \
    ServiceState, generate_sbi_config
from config_db.config_db_redis import ConfigDb
from _version import __version__

LOG = logging.getLogger('sip.tango_control.SDPMaster')


class SDPMasterDevice(Device):
    """SIP SDP Master device."""

    _start_time = time.time()
    _service_state = ServiceState('TangoControl', 'SDPMaster', __version__)
    _sdp_state = SDPState()

    # -------------------------------------------------------------------------
    # General methods
    # -------------------------------------------------------------------------
    def init_device(self):
        """Device constructor."""
        Device.init_device(self)
        self._set_master_state('init')

        # Add anything here that has to be done before the device is set to
        # its ON state.

        self._set_master_state('on')

    def always_executed_hook(self):
        """Run for each command."""
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
        print(value)

        ConfigDb().flush_db()
        sbi_config = generate_sbi_config(register_workflows=True)
        sbi = SchedulingBlockInstance.from_config(sbi_config)
        pb_list = sbi.processing_block_ids
        print('PB_LIST', pb_list)
        active_pbs = ProcessingBlockList.active
        print('ACTIVE', active_pbs)

        # Get a PB device which has not been assigned.
        for pb in pb_list:
            for index in range(100):
                pb_dev = 'sip_sdp/pb/{:03d}'.format(index)
                device = DeviceProxy(pb_dev)
                if not device.pb_id:
                    LOG.info('Assigning PB device = %s to PB id = %s',
                             device.name(), pb)
                    device.pb_id = pb
                    break

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
        return __version__

    @attribute(dtype=str)
    def current_sdp_state(self):
        """Return the current state of the SDP."""
        return self._sdp_state.current_state

    @attribute(label="Target", dtype=str)
    def target_sdp_state(self):
        """Return the target state of SDP."""
        return self._sdp_state.target_state

    @target_sdp_state.write
    def target_sdp_state(self, new_state):
        """Update the target state of SDP."""
        self._sdp_state.update_target_state(new_state)

    @attribute(dtype=float)
    @DebugIt()
    def health_check(self):
        """Health check method, returns the up-time of the device."""
        return time.time() - self._start_time

    @attribute(dtype=str)
    def resource_availability(self):
        """Return the a JSON dict describing the SDP resource availability."""
        return json.dumps(dict(nodes_free=randrange(1, 500)))

    # @pipe
    # def resource_availability(self):
    #     """Return the a dict describing the SDP resource availability."""
    #     return 'resource_availability', dict(nodes_free=randrange(1, 500))

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

    def _set_master_state(self, state):
        """Set the state of the SDPMaster."""
        if state == 'init':
            self.set_state(DevState.INIT)
            if self._service_state.current_state == 'on':
                LOG.debug('%s is already on! (cant be reinitialised)',
                          self._service_state.id)
                return
            try:
                self._service_state.update_current_state('init')
            except ValueError as error:
                LOG.warning('%s', str(error))

        elif state == 'on':
            self.set_state(DevState.STANDBY)
            self._service_state.update_current_state('on')
