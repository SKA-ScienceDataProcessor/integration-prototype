# -*- coding: utf-8 -*-
"""Module for generating visibility recv compose files."""

import json

from .utils import load_template, validate_config, load_json_file


def generate(config):
    """Generate Docker compose file for the visibility ingest workflow stage.

    This is expected to be run using Docker Swarm as an Execution Engine.

    Args:
        config (dict): Workflow stage configuraion.

    Return:
        string, Docker compose file string for use with Docker Swarm.

    """
    # Validate the workflow stage configuration
    validate_config(config, stage_type='vis_ingest', ee_type='docker_swarm')

    # Get local configuration object references
    ee_config = config['ee_config']
    app_config = config['app_config']

    # TODO(BM) Validate the ee and app configuration schema

    app_args_file = app_config['command_args']['json_file']
    json_args = json.dumps(load_json_file(app_args_file))

    template_params = dict(
        json_config=json_args,
        buffer_path=ee_config['buffer_path'],
        num_receivers=ee_config['num_receivers']
    )

    # Render the compose template for the ingest serivce configuraion
    compose_template = load_template(ee_config['compose_template'])
    compose_file = compose_template.render(**template_params)

    return compose_file
