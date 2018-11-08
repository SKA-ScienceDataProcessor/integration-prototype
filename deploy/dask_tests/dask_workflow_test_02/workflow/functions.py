# -*- coding: utf-8 -*-
"""."""
import logging
import time
from astropy.cosmology import WMAP9 as cosmo

LOG = logging.getLogger('SIP.W')

def set_value(x):
    LOG.info('Setting value...')
    return cosmo.H(0).value

def square(x):
    time.sleep(500.0)
    return x**2

def neg(x):
    time.sleep(500.0)
    return -x
