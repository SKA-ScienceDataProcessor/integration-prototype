# coding=utf-8
"""Module to set up workflow variables for demo 3."""
import json
import logging
import time
from os.path import join
from subprocess import call

from tango import DeviceProxy

from sip_logging import init_logger

init_logger()
log = logging.getLogger('sip.itango_utils.load_sbi_config')

sbi_config_file = join('data', 'sbi_config.json')
with open(sbi_config_file, 'r') as file:
    sbi_config_str = file.read()
sbi_config_dict = json.loads(sbi_config_str)

md = DeviceProxy('sip_sdp/elt/master')
md.target_sdp_state = 'on'
while md.current_sdp_state != 'on':
    time.sleep(0.1)

if md.current_sdp_state == 'on':
    sbi_ids = json.loads(md.scheduling_block_instances).get('active')
    pb_ids = json.loads(md.processing_blocks).get('active')
    if sbi_ids:
        num_sbis = len(sbi_ids)
        num_pbs = len(sbi_ids)
        new_sbi_id = 'SBI-20181123-sip-demo-{:03d}'.format(num_sbis + 1)
        new_pb_id = 'PB-20181123-sip-demo-{:03d}'.format(num_pbs + 1)
        sbi_config_dict['id'] = new_sbi_id
        sbi_config_dict['processing_blocks'][0]['id'] = new_pb_id
    log.info('configuring %s', sbi_config_dict['id'])
    md.configure(json.dumps(sbi_config_dict))
