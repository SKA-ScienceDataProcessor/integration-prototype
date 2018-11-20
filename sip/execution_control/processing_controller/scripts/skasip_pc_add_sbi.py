#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Utility module to add an SBI to the config database."""
import json

from os.path import dirname, join
from sip_config_db import LOG
from sip_logging import init_logger
from sip_config_db.scheduling import SchedulingBlockInstance
from ..tests.test_utils import add_workflow_definitions


def main():
    """Main function."""
    data_dir = join(dirname(__file__), '../tests/data')
    add_workflow_definitions(join(data_dir, 'workflow_definitions'))
    with open(join(data_dir, 'sbi_config_2.json')) as _file:
        sbi_config = json.load(_file)
    sbi = SchedulingBlockInstance.from_config(sbi_config)
    LOG.info('Added offline only SBI: %s', sbi.id)


if __name__ == '__main__':
    init_logger()
    main()
