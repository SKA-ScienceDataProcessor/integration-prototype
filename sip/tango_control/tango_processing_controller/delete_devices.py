#!/usr/bin/python3
"""Delete Processing Block devices from the TANGO Database."""
import logging

from sip_logging import init_logger
from tango import Database


def delete_pb_devices():
    """Register PBs devices.

    Note(BMo): Ideally we do not want to register any devices here. There
    does not seem to be a way to create a device server with no registered
    devices in Tango. This is probably because Tango devices must have been
    registered before the server starts ...
    """
    log = logging.getLogger('sip.tango_control.subarray')
    tango_db = Database()
    log.info("Deleting PB devices:")

    for index in range(1000):
        name = 'sip_sdp/pb/PB-{:03d}'.format(index)
        log.info("\t%s", name)
        tango_db.delete_device(name)

    # tango_db.add_server(dev_info.server, dev_info, with_dserver=True)
    # tango_db.delete_device(dev_info.name)


if __name__ == '__main__':
    init_logger()
    delete_pb_devices()
