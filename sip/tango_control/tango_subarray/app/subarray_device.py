# -*- coding: utf-8 -*-
"""Tango subarray device class."""
import json
import time

import jsonschema
from tango import DebugIt, DevState
from tango.server import Device, attribute, class_property, command, pipe

from sip_config_db.scheduling import SchedulingBlockInstance, Subarray


class SubarrayDevice(Device):
    """SDP Subarray device class."""

    def init_device(self):
        """Initialise the device."""
        Device.init_device(self)
        time.sleep(0.1)
        self.set_state(DevState.STANDBY)

    version = class_property(dtype=str, default_value='test')

    @command(dtype_in=str, dtype_out=str)
    @DebugIt()
    def configure(self, sbi_config: str):
        """Configure an SBI for this subarray.

        Args:
            sbi_config (str): SBI configuration JSON

        Returns:
            str,

        """
        # print(sbi_config)
        config_dict = json.loads(sbi_config)
        self.debug_stream('SBI configuration:\n%s',
                          json.dumps(config_dict, indent=2))
        try:
            sbi = Subarray(self.get_name()).configure_sbi(config_dict)
        except jsonschema.exceptions.ValidationError as error:
            return json.dumps(dict(path=error.absolute_path.__str__(),
                                   schema_path=error.schema_path.__str__(),
                                   message=error.message), indent=2)
        except RuntimeError as error:
            return json.dumps(dict(error=str(error)), indent=2)
        return 'Accepted SBI: {}'.format(sbi.id)

    @command
    def abort(self):
        """Abort all SBIs (and PBs) for this subarray."""

    @command()
    def deactivate(self):
        """Deactivate the subarray."""
        Subarray(self.get_name()).deactivate()

    @command
    def activate(self):
        """Activate the subarray."""
        Subarray(self.get_name()).activate()

    @attribute(dtype=bool)
    def active(self):
        """Return true if the subarray is active."""
        return Subarray(self.get_name()).active

    @attribute(dtype=str)
    def id(self):
        """Return the device id."""
        return self.get_name()

    @pipe
    def scheduling_block_instances(self):
        """Return list of SBIs associated with this subarray."""
        return 'SBI', Subarray(self.get_name()).sbi_ids

    @pipe
    def processing_blocks(self):
        """Return list of PBs associated with the subarray.

        <http://www.esrf.eu/computing/cs/tango/pytango/v920/server_api/server.html#PyTango.server.pipe>
        """
        sbi_ids = Subarray(self.get_name()).sbi_ids
        pbs = []
        for sbi_id in sbi_ids:
            sbi = SchedulingBlockInstance(sbi_id)
            pbs.append(sbi.processing_block_ids)
        return 'PB', pbs
