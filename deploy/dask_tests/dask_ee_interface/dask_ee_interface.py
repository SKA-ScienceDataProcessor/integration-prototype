# -*- coding: utf-8 -*-
"""Some experiments to put together an EE interface for Dask."""
import time
import os
import logging
import sys
import subprocess
import json
import yaml
import docker

from pprint import pprint
from dask.distributed import Client, progress, Scheduler, Executor, Future
import distributed.scheduler


LOG = logging.getLogger('SIP.DASK_EE_INTERFACE')


def start_dask_ee(config):
    """Start the Dask EE containers for the workflow.

    Args:
        config (dict): Workflow configuration dictionary
    """
    docker_client = docker.from_env()

    # 1. Load and run the dask EE compose file
    ee_compose_file = os.path.join('..', 'dask_workflow_test_02',
                                   'docker-compose.hostnet.ee.yml')
    with open(ee_compose_file, 'r') as file:
        # Load the compose file into a configuration dictionary.
        try:
            ee_config = yaml.load(file)
        except yaml.YAMLError as error:
            LOG.critical('%s', error)

        # print(json.dumps(config, indent=2))
        LOG.info('Creating networks:')
        LOG.info('%s', '-' * 80)
        for network, config in ee_config['networks'].items():
            LOG.info('Network name: %s', network)
            LOG.debug('Network config: %s', config)
            try:
                network = docker_client.networks.get(config['name'])
                LOG.debug('Network \'%s\' found! (id=%s)',
                          config['name'], network.short_id)
                # TODO(BM) check that the network is parameters match.
                # LOG.debug(network.attrs)
            except docker.errors.NotFound:
                LOG.critical('Network \'%s\' not found!', config['name'])
                if config['external']:
                    pass
                else:
                    pass
                    # network = docker_client.networks.get(config['name'])
                    # print(network.id)
                    # network = docker_client.networks.create(
                    #     name=config['name'],
                    # )
        LOG.info('')
        LOG.info('Creating Services:')
        LOG.info('%s', '-' * 80)
        for service, config in ee_config['services'].items():
            LOG.info('Service name: %s', service)
            LOG.debug('Service config: %s', config)
            LOG.debug('Service image: %s', config['image'])
            LOG.debug('Service networks: %s', config['networks'])
            _deploy = config['deploy']
            LOG.debug('Service resources: %s', _deploy['resources'])
            LOG.debug('Service replicas: %s', _deploy[''])
            # LOG.debug('Service constaints: %s', ...)

            # service_mode = docker.types.ServiceMode(mode='replicated',
            #                                         replicas=1)
            # resources = docker.types.Resources()
            # restart_policy = docker.types.RestartPolicy(condition='none')

            # service = docker_client.services.create(
            #     image=config['image'],
            #     # name=config['name'],
            #     restart_policy=docker.types.RestartPolicy(condition='none'),
            #     networks=''
            # )


def start_workflow(config):
    """Start the workflow.

    1. Deploy a container to initialise logging with restart mode = False
    2. Deploy a container to run the workflow (or workflow stage).
    3. Return the container ID of the workflow and EE (scheduler + worker)
       containers. This info should be added to a backing store (eg config
       database) for tracking.

    Args:
        config (dict): Workflow configuration dictionary.
    """
    # 1. Load the run the dask workflow image

    # In order not to have to return handles, use service names which can be
    # regenerated based on entries in the configuration.


def stop(config):
    """Stop the workflow stage

    Tear down the containers

    Args:
        config (dict): Workflow configuration dictionary.
    """
    # While it is possible to call cancel on the client that requires that the
    # list of futures is known to the wrapper.
    # Therefore just kill the process?

    # Find service ids for the workflow
    # Kill services

def status(config):
    """Get the status of the workflow stage.

    First check if the containers are running.

    Then queury the Dask scheduler.

    Args:
        config (dict): Workflow configuraiton dictionary.
    """
    # This can be queried more easily by various client functions.
    # 'PENDING', 'RUNNING', ' FINISHED', 'ERROR', 'WARNING' ?
    # This can be defined by the adapter


def main():
    """."""
    # <https://distributed.readthedocs.io/en/latest/scheduling-state.html#distributed.scheduler.Scheduler>

    start_dask_ee({})


    # client = Client('localhost:8786')
    # client.run(init_logging)
    # client.run_on_scheduler(init_logging)
    # start({})

    # Get the list of running futures
    # client = Client('localhost:8786')

    # # print(client.processing())
    # p = client.processing()
    # for tasks in p.values():
    #     for task in tasks:
    #         f = Future(task)
    #         f.cancel()
    #         print(task, f.done())

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
    LOG.addHandler(logging.StreamHandler(sys.stdout))
    LOG.setLevel('DEBUG')
    main()
