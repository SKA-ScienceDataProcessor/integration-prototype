# -*- coding: utf-8 -*-
"""SKA SDP Master Device prototype.

TODO(BMo): Exception handling if the config database is dead.

"""
# pylint: disable=no-self-use
import json
import time
from random import randrange

from tango import Database, DebugIt, DevState, DeviceProxy
from tango.server import Device, attribute, command

from release import LOG, __service_name__, __subsystem__, __version__
from sip_config_db.scheduling import ProcessingBlockList, \
    SchedulingBlockInstance, SchedulingBlockInstanceList
from sip_config_db.states import SDPState, ServiceState
from sip_config_db.states.services import get_service_id_list, \
    get_service_state_list


class SDPMasterDevice(Device):
    """SIP SDP Master device."""

    _start_time = time.time()
    _service_state = ServiceState(__subsystem__, __service_name__,
                                  __version__)
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

        # Only accept new SBIs if the SDP is on.
        if self._sdp_state.current_state != 'on':
            raise RuntimeWarning('Unable to configure SBIs unless SDP is '
                                 '\'on\'.')

        # Check that the new SBI is not already registered.
        sbi_config_dict = json.loads(value)
        sbi_list = SchedulingBlockInstanceList()
        LOG.info('SBIs before: %s', sbi_list.active)
        if sbi_config_dict.get('id') in sbi_list.active:
            raise RuntimeWarning('Unable to add SBI with ID {}, an SBI with '
                                 'this ID is already registered with SDP!'
                                 .format(sbi_config_dict.get('id')))

        # Add the SBI to the dictionary.
        LOG.info('Scheduling offline SBI! Config:\n%s', value)
        sbi = SchedulingBlockInstance.from_config(sbi_config_dict)
        LOG.info('SBIs after: %s', sbi_list.active)

        sbi_pb_ids = sbi.processing_block_ids
        LOG.info('SBI "%s" contains PBs: %s', sbi.id, sbi_pb_ids)
        # pb_list = ProcessingBlockList()
        # LOG.info('Active PBs: %s', pb_list.active)

        # Get the list and number of Tango PB devices
        tango_db = Database()
        pb_device_class = "ProcessingBlockDevice"
        pb_device_server_instance = "processing_block_ds/1"
        pb_devices = tango_db.get_device_name(pb_device_server_instance,
                                              pb_device_class)
        LOG.info('Number of PB devices in the pool = %d', len(pb_devices))

        # Get a PB device which has not been assigned.
        for pb_id in sbi_pb_ids:
            for pb_device_name in pb_devices:
                device = DeviceProxy(pb_device_name)

                if not device.pb_id:
                    LOG.info('Assigning PB device = %s to PB id = %s',
                             pb_device_name, pb_id)
                    # Set the device attribute 'pb_id' to the processing block
                    # id it is tracking.
                    device.pb_id = pb_id
                    break

    @staticmethod
    def _get_service_state(service_id: str):
        """Get the Service state object for the specified id."""
        LOG.debug('Getting state of service %s', service_id)
        services = get_service_id_list()
        service_ids = [s for s in services if service_id in s]
        if len(service_ids) != 1:
            return 'Service not found! services = {}'.format(str(services))
        subsystem, name, version = service_ids[0].split(':')
        return ServiceState(subsystem, name, version)

    @command(dtype_in=str, dtype_out=str)
    @DebugIt()
    def get_current_service_state(self, service_id: str):
        """Get the state of a SDP service."""
        state = self._get_service_state(service_id)
        return state.current_state

    @command(dtype_in=str, dtype_out=str)
    @DebugIt()
    def get_target_service_state(self, service_id: str):
        """Get the state of a SDP service."""
        state = self._get_service_state(service_id)
        return state.target_state

    # ------------------
    # Attributes methods
    # ------------------

    @attribute(dtype=str)
    def version(self):
        """Return the version of the Master Controller Device."""
        return __version__

    @attribute(dtype=str)
    def sdp_services(self):
        """Return list of SDP services."""
        services = get_service_state_list()
        return str(services)

    @attribute(dtype=str)
    def current_sdp_state(self):
        """Return the current state of the SDP."""
        return self._sdp_state.current_state

    @attribute(label="Target", dtype=str)
    def target_sdp_state(self):
        """Return the target state of SDP."""
        return self._sdp_state.target_state

    @attribute(dtype=str)
    def allowed_target_sdp_states(self):
        """Return a list of allowed target states for the current state."""
        _current_state = self._sdp_state.current_state
        _allowed_target_states = self._sdp_state.allowed_target_states[
            _current_state]
        return json.dumps(dict(allowed_target_sdp_states=
                               _allowed_target_states))

    @target_sdp_state.write
    def target_sdp_state(self, state):
        """Update the target state of SDP."""
        LOG.info('Setting SDP target state to %s', state)
        if self._sdp_state.current_state == state:
            LOG.info('Target state ignored, SDP is already "%s"!', state)
        if state == 'on':
            self.set_state(DevState.ON)
        if state == 'off':
            self.set_state(DevState.OFF)
        if state == 'standby':
            self.set_state(DevState.STANDBY)
        if state == 'disable':
            self.set_state(DevState.DISABLE)
        self._sdp_state.update_target_state(state)

    @attribute(dtype=str)
    @DebugIt()
    def health(self):
        """Health check method, returns the up-time of the device."""
        return json.dumps(dict(uptime='{:.3f}s'
                               .format((time.time() - self._start_time))))

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
        sbi_list = SchedulingBlockInstanceList()
        return json.dumps(dict(active=sbi_list.active,
                               completed=sbi_list.completed,
                               aborted=sbi_list.aborted))

    @attribute(dtype=str)
    def processing_blocks(self):
        """Return the a JSON dict encoding the PBs known to SDP."""
        pb_list = ProcessingBlockList()
        # TODO(BMo) realtime, offline etc.
        return json.dumps(dict(active=pb_list.active,
                               completed=pb_list.completed,
                               aborted=pb_list.aborted))

    @attribute(dtype=str)
    def processing_block_devices(self):
        """Get list of processing block devices."""
        # Get the list and number of Tango PB devices
        tango_db = Database()
        pb_device_class = "ProcessingBlockDevice"
        pb_device_server_instance = "processing_block_ds/1"
        pb_devices = tango_db.get_device_name(pb_device_server_instance,
                                              pb_device_class)
        LOG.info('Number of PB devices in the pool = %d', len(pb_devices))

        pb_device_map = []
        for pb_device_name in pb_devices:
            device = DeviceProxy(pb_device_name)
            if device.pb_id:
                LOG.info('%s %s', pb_device_name, device.pb_id)
                pb_device_map.append((pb_device_name, device.pb_id))

        return str(pb_device_map)

    def _set_master_state(self, state):
        """Set the state of the SDPMaster."""
        if state == 'init':
            self._service_state.update_current_state('init', force=True)
            self.set_state(DevState.INIT)

        elif state == 'on':
            self.set_state(DevState.ON)
            self._service_state.update_current_state('on')
