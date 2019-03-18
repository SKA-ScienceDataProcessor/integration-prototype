# coding=utf-8
"""Module to get tango device variables."""
import logging
from sip_logging import init_logger
from tango import DeviceProxy

init_logger()
log = logging.getLogger('sip.itango_utils.get_tango_devices')

device_name = 'sip_sdp/elt/master'
log.info('* Getting Tango Master Device (%s) as: \'md\'', device_name)
md = DeviceProxy(device_name)
log.info('  - Tango Master Device version: %s, status: %s', md.version,
         md.status())
log.info('* Tango Master Device attributes:')
for attr in md.get_attribute_list():
    log.info('  - %s', attr)
log.info('* Tango Master Device commands:')
for cmd in md.get_command_list():
    log.info('  - %s', cmd)


sub = []
for index in range(2):
    device_name = 'sip_sdp/elt/subarray_{:02d}'.format(index)
    log.info('* Getting Subarray %02d Device (%s) as: \'sub[%02d]\'',
             index, device_name, index)
    device = DeviceProxy(device_name)
    # sub.append(DeviceProxy('sip_sdp/elt/subarray_%02d'.format(index)))
    # log.info('  - Subarray %02d Device version: %s, status: %s',
    #          sub[index].version, sub[index].status())
