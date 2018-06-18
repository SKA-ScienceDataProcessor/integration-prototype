# -*- coding: utf-8 -*-
"""Test workflow for playing around with Dask deployment options"""
import logging
import time
from dask.distributed import Client, progress
import os
import sys
from .functions import set_value, square, neg


def init_logging():
    """."""
    log = logging.getLogger('')
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel('DEBUG')
    handler.setFormatter(logging.Formatter('[%(name)s] -- %(message)s'))
    log.addHandler(handler)
    log.setLevel('DEBUG')

    log = logging.getLogger('SIP')
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel('DEBUG')
    handler.setFormatter(logging.Formatter('[%(name)s] -- %(message)s'))
    log.addHandler(handler)
    log.setLevel('DEBUG')


def print_listdir(x):
    """."""
    log = logging.getLogger('SIP.workflow.function')
    log.info('HERE A')
    print('Task id = {} {}'.format(x, os.listdir('.')))
    return x, os.listdir('.')


def print_values(x):
    """."""
    log = logging.getLogger('SIP')
    time.sleep(10)
    print('Print Values ........', x)
    print('x' * 20)
    log.debug('HERE B')
    return x


def main():
    """."""
    host = os.getenv('DASK_SCHEDULER_HOST', default='localhost')
    port = os.getenv('DASK_SCHEDULER_PORT', default=8786)
    client = Client('{}:{}'.format(host, port))
    # client.run(init_logging)
    # client.run_on_scheduler(init_logging)

    # Run some mock functions and gather a result
    data = client.map(print_listdir, range(10))
    future = client.submit(print_values, data)
    progress(future)
    print('')
    result = client.gather(future)
    print(result)

    # Run a second stage which runs some additional processing.
    print('here A')
    data_a = client.map(set_value, range(100))
    print('here B')
    data_b = client.map(square, data_a)
    print('here C')
    data_c = client.map(neg, data_b)
    print('here D')
    # Submit a function application to the scheduler
    total = client.submit(sum, data_c)
    print('here E')
    progress(total)
    print(total.result())
    print('here F')
