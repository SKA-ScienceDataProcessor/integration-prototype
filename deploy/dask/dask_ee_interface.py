# -*- coding: utf-8 -*-
"""."""
import time
import logging
import sys
from pprint import pprint
from dask.distributed import Client, progress, Scheduler, Executor, Future
import distributed.scheduler
import subprocess

# <http://distributed.readthedocs.io/en/latest/api.html#distributed.client.Client.get>
# https://stackoverflow.com/questions/41111889/how-to-terminate-workers-started-by-dask-multiprocessing-scheduler?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa

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
    pid = subprocess.Popen(['python3', '-m', 'workflow'])
    print(pid)
    # In order for this to be stateless, it will be necessary to hold
    # the PID in the config database?
    # Could also have the work stopped by tearing down all of the containers
    # containing the workflow.

    # Options:
    # 1. Popen
    # 2. Have the workflow code not need the client and have the client defined
    #    only in the wrapper. Workflow code is then run against the client.
    # 3. Pass the client to the workflow
    # 4. Start a container which contains the workflow and have this run the
    #    workflow when started. To stop the workflow kill the workflow container

    # --- Number 4 might be the best option.



def stop(config):
    """Stop the workflow stage"""
    # While it is possible to call cancel on the client that requires that the
    # list of futures is known to the wrapper.
    # Therefore just kill the process?


def status(config):
    """Get the status of the workflow stage"""
    # This can be queried more easily by various client functions.
    # 'PENDING', 'RUNNING', ' FINISHED', 'ERROR', 'WARNING' ?
    # This can be defined by the adapter




def main():
    """."""
    # <https://distributed.readthedocs.io/en/latest/scheduling-state.html#distributed.scheduler.Scheduler>

    # client = Client('localhost:8786')
    # client.run(init_logging)
    # client.run_on_scheduler(init_logging)
    # start({})

    # Get the list of running futures
    client = Client('localhost:8786')

    # print(client.processing())
    p = client.processing()
    for tasks in p.values():
        for task in tasks:
            f = Future(task)
            f.cancel()
            print(task, f.done())




    # stack = client.call_stack()
    # for s in stack:
    #     while len(stack[s]) > 0:
    #         print(len(stack[s]))
    #         for x in stack[s]:
    #             print(x)
    #             f = Future(x)
    #             f.cancel()
    #             print(f.done())


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
