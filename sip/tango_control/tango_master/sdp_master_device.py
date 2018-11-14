# -*- coding: utf-8 -*-
"""SKA SDP Master Device prototype."""
import json
import time
import logging
from random import randrange

from _version import __version__
from config_db import ProcessingBlock, ProcessingBlockList, SDPState, \
    SchedulingBlockInstanceList, ServiceState, generate_sbi_config, \
    SchedulingBlockInstance
from config_db.config_db_redis import ConfigDb
from tango import Database, DbDevInfo, DebugIt, DevState, Util
from tango import DeviceProxy
from tango.server import Device, DeviceMeta, attribute, command


LOG = logging.getLogger('sip.tango_control.SDPMaster')


class SDPMasterDevice(Device):
    """SIP SDP Master device."""

    _start_time = time.time()
    _service_state = ServiceState('TangoControl', 'SDPMaster', __version__)

    # -------------------------------------------------------------------------
    # General methods
    # -------------------------------------------------------------------------
    def init_device(self):
        """Device constructor."""
        Device.init_device(self)
        self._set_state('init')

        # FIXME(BMo) blocking wait until all other SDP services are online.
        time.sleep(5)

        self._set_state('standby')

    def always_executed_hook(self):
        """FIXME Add docstring."""
        print('always executed hook!')
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

    def _set_state(self, state):
        """Set the state of the SDPMaster."""
        if state == 'init':
            self._set_state(DevState.INIT)
            # FIXME(BMo) Updating the current state to init should \
            #            be allowed if already in init!
            self._service_state.update_current_state('init')

        elif state == 'standby':
            self._set_state(DevState.STANDBY)
            self._service_state.update_current_state('standby')
