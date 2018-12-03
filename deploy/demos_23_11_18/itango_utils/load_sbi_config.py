# coding=utf-8
"""Utility module to load SBI configuration strings.

Run with:
    %run itango_utils/load_sbi_config.py
"""
import json
from os.path import join
import logging
from sip_logging import init_logger

init_logger()
log = logging.getLogger('sip.itango_utils.load_sbi_config')

sbi_config_file = join('data', 'sbi_config.json')
log.info('* Loading: %s', sbi_config_file)
with open(sbi_config_file, 'r') as file:
    sbi_config_str = file.read()
sbi_config_dict = json.loads(sbi_config_str)
log.info('* File loaded as: \'sbi_config_dict\'')
