# -*- coding: utf-8 -*-
"""Module for generating visibility send compose files.

Handles the contents of a workflow stage of type 'csp_vis_emulator'.
"""
import json

from .utils import validate_config, load_template


def generate(config):
    """Generate a Docker compose file for the CSP Visibility emulator.

    This is expected to be run using Docker Swarm as an Execution Engine.

    Args:
        config (dict): Workflow stage configuration

    Returns:
        string, Docker compose file string for use with Docker Swarm.

    """
    # Validate the workflow stage configuration.
    validate_config(config, stage_type='csp_vis_emulator',
                    ee_type='docker_swarm')

    # Get local configuration object references
    ee_config = config['ee_config']
    app_config = config['app_config']

    # TODO(BM) Validate the ee and app configuration schema

    # Load the application command line args template
    app_template = app_config['command_args']['template']
    app_template = load_template(app_template)

    # Check the number of senders matches the number of host ip's specified
    num_senders = ee_config['num_senders']
    if num_senders != len(app_config['destination_hosts']):
        raise RuntimeError('Sender destination hosts configuration '
                           'needs to match the number of senders.')

    # Generate configuration for each sender service.
    senders = []
    # FIXME(BM) may need service names to be (globally) unique? \
    # (if so will have to pass in extra information such as the PB id)
    for i in range(ee_config['num_senders']):
        app_template_vars = dict(
            destination_host=app_config['destination_hosts'][i],
            destination_port_start=app_config['destination_port_start']
        )
        command = json.loads(app_template.render(**app_template_vars))
        sender = dict(
            service_name='sender{:03d}'.format(i),
            id='sender{:03d}'.format(i),
            command=json.dumps(command))
        senders.append(sender)

    # Render the compose template for the generated sender service configuration
    compose_template = load_template(ee_config['compose_template'])
    compose_file = compose_template.render(senders=senders)

    return compose_file
