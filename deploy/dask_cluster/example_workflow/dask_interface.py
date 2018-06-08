# -*- coding: utf-8 -*-
"""."""
import time
import logging
import sys
from pprint import pprint
from dask.distributed import Client, progress, Scheduler, Executor, Future
import distributed.scheduler

# <http://distributed.readthedocs.io/en/latest/api.html#distributed.client.Client.get>


def init_logging():
    """."""
    # TODO(BM) prevent loggers from being defined more than once \
    # if this function is called several times.
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

    log.info('Initialised ROOT logger')
    log.info('Initialised SIP logger')


def start(config):
    """Start the workflow stage"""
    # Probably just have to perform a syscall to run the python script and get a
    # processes handle to kill it?


def stop(config):
    """Stop the workflow stage"""
    # While it is possible to call cancel on the client that requires that the
    # list of futures is known to the wrapper.
    # Therefore just kill the process?


def status(config):
    """Get the status of the workflow stage"""
    # This can be queried more easily by various client functions.


def main():
    """."""
    # <https://distributed.readthedocs.io/en/latest/scheduling-state.html#distributed.scheduler.Scheduler>

    client = Client('localhost:8786')
    stack = client.call_stack()
    for s in stack:
        print(s)
        for x in stack[s]:
            print(x)
            f = Future(x)
            print(f.done())


    # pprint(client.call_stack())
    # client.run(init_logging)
    # client.run_on_scheduler(init_logging)

    # executor = client.get_executor()
    # print(client.done())
    # scheduler = client.scheduler
    # print(type(scheduler))
    # print(scheduler.status)
    # print(scheduler.)
    # scheduler.run_function(main)
    # from workflow.workflow import main
    # future = client.submit(main, client)
    # progress(future)
    # while not future.done():
    #     print('waiting ...')
    #     time.sleep(0.5)


    # Need to spawn a thread to manage the workflow?
    # Could also add a callback with add_done_callback?
    # future = start({})
    # # print(future.result())
    # timeout = 30
    # timer = time.time()
    # while not future.done():
    #     print(future.done())
    #     time.sleep(0.5)
    #     if time.time() - timer > timeout:
    #         print('TIMEOUT')
    #         future.cancel()

    # <http://distributed.readthedocs.io/en/latest/api.html>
    # client = Client('localhost:8786')
    # print("-------------------------------")
    # print('SCHEDULER LOGS')
    # pprint(client.get_scheduler_logs())
    # print("-------------------------------")
    # print('NCORES')
    # print(client.ncores())
    # print("-------------------------------")
    # print('CLIENT PROFILE')
    # pprint(client.profile())
    # print("-------------------------------")
    # print('SCHEDULER_INFO')
    # pprint(client.scheduler_info())
    # print("-------------------------------")
    # print('HAS_WHAT')
    # pprint(client.has_what())
    # print("-------------------------------")


if __name__ == '__main__':
    main()
