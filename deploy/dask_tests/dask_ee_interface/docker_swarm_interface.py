# -*- coding: utf-8 -*-
"""Experimental Docker Swarm EE interface adapter."""
import os
import pprint
import json
import yaml


def read_compose_file(path, filename='docker-compose.yml'):
    """Read a compose file."""
    filepath = os.path.join(path, filename)
    with open(filepath, "r") as _file:
        try:
            config = yaml.load(_file)
            # print(json.dumps(config, indent=2))
            return config
        except yaml.YAMLError as error:
            print(error)
            raise


def create_networks(config):
    """Create networks."""


def start_services(config):
    """Create networks."""


def stop_services(config):
    """Stop services."""


def destroy_networks(config):
    """Destroy user defined networks."""


def get_status(config):
    """Return the status."""


def main():
    """."""
    path = os.path.join('..', 'dask_workflow_test_02')
    config = read_compose_file(path)
    print(json.dumps(config, indent=2))
    print('-' * 80)
    for service, service_desc in config['services'].items():
        print(service)
        print(service_desc)



if __name__ == '__main__':
    main()
