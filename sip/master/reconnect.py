# coding: utf-8

from sip.common.logging_api import log
from sip.master.config import slave_config_dict
from sip.master import slave_control

def reconnect(paas):
    """ Function that tries to reconnect to running services
    """
    # Go through all the "online" services in the slave map see if
    # the corresponding service is running
    for name, config in slave_config_dict().items():
        if config['online']:

            # Try to get a descriptor for the service
            descriptor = paas.find_task(name)
            if descriptor:
                try:
                    log.info('Attempting to reconnect to {}'.format(name))
                    slave_control.reconnect(name, descriptor)
                except:
                    pass
