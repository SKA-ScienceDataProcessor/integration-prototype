# -*- coding: utf-8 -*-
"""Module for startup test compose files."""

import json

from .utils import load_template, validate_config, load_json_file


def generate(config):
    """Generate Docker compose file for startup workflow stage.

    This is expected to be run using Docker Swarm as an Execution Engine.

    Args:
        config (dict): Workflow stage configuration.

    Return:
        string, Docker compose file string for use with Docker Swarm.

    """
    # Validate the workflow stage configuration
    validate_config(config, stage_type='processing', ee_type='docker_swarm')

    # Get local configuration object references
    ee_config = config['ee_config']
    app_config = config['app_config']

    # TODO(BM) Validate the ee and app configuration schema

    app_args_file = app_config['compose_template']
    json_args = json.dumps(load_json_file(app_args_file))

    template_params = dict(
        # json_config=json_args,
        buffer_path="/app"
    )

    # Render the compose template for the ingest service configuration
    # TODO this wil eventually comes from DB
    compose_template = load_template(ee_config['compose_template'])

    compose_file = compose_template.render(**template_params)

    return compose_file
