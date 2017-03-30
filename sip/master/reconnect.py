# coding: utf-8

from sip.common.logging_api import log
from sip.master import config
from sip.master import slave_control

def reconnect(paas):
    """ Function that tries to reconnect to running services
    """
    # Go through all the "online" services in the slave map see if
    # the corresponding service is running
    for name, cfg in config.slave_config.items():
        if cfg['online']:

            # Get a descriptor for the service
            descriptor = paas.find_task(name)
            if descriptor:
                log.info('Attempting to reconnect to {}'.format(name))
                slave_control.reconnect(name, descriptor)

