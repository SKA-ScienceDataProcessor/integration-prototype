#!/usr/bin/python3
"""Register Processing Controller devices with the TANGO Database."""
import logging

from sip_logging import init_logger
from tango import Database, DbDevInfo


def register_pb_devices():
    """Register PBs devices.

    Note(BMo): Ideally we do not want to register any devices here. There
    does not seem to be a way to create a device server with no registered
    devices in Tango. This is probably because Tango devices must have been
    registered before the server starts ...
    """
    log = logging.getLogger('sip.tango_control.subarray')
    tango_db = Database()
    log.info("Registering PB devices:")
    dev_info = DbDevInfo()
    # pylint: disable=protected-access
    dev_info._class = 'ProcessingBlockDevice'
    dev_info.server = 'processing_controller_ds/1'

    for index in range(100):
        dev_info.name = 'sip_sdp/pb/PB-{:03d}'.format(index)
        log.info("\t%s", dev_info.name)
        tango_db.add_device(dev_info)

    # tango_db.add_server(dev_info.server, dev_info, with_dserver=True)
    # tango_db.delete_device(dev_info.name)


if __name__ == '__main__':
    init_logger()
    register_pb_devices()
