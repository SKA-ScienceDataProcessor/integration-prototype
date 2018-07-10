# -*- coding: utf-8 -*-
"""Module for dynamically generating Docker compose files.

Generates Docker compose files for use with Docker Swarm
(`docker stack deploy` or equivalent) based on Jinja2 templates.
"""
import logging

import jinja2

from .compose_generators.vis_send import generate as generate_vis_send
from .compose_generators.vis_recv import generate as generate_vis_recv


LOG = logging.getLogger('sip.ee_interface.docker_compose_generator')


def _validate_workflow_config(config):
    """Validate the workflow configuration.

    Args:
        config (dict): Workflow stage configuration dictionary.

    Raises:
        RuntimeError, if the configuration is invalid.
    """
    # Validate the configuration.
    if 'type' not in config:
        raise RuntimeError('Workflow stage type not found in '
                           'configuration.')

    if 'ee_config' not in config:
        raise RuntimeError('Execution engine configuration not found in '
                           'configuration.')

    if 'app_config' not in config:
        raise RuntimeError('Application engine configuration not found in '
                           'configuration.')


def generate_compose_file(config):
    """Dynamically generate Docker compose file.

    This converts a workflow stage configuration dictionary,
    stored in the Configuration Database, into a Docker Compose file
    string that can be used to execute a workflow stage using
    the SIP Docker Swarm client library.

    Args:
        config (dict): Workflow stage configuration dictionary.
    """
    _validate_workflow_config(config)

    # Swtich on the type of the workflow stage
    stage_type = config['type']
    if stage_type == 'csp_vis_emulator':
        LOG.debug('Generating CSP visibility emulator Docker configuration')
        compose_file = generate_vis_send(config)
    elif stage_type == 'vis_recv':
        LOG.debug('Generating visibility ingest Docker configuration')
        compose_file = generate_vis_recv(config)
    elif stage_type == 'test':
        raise NotImplementedError
    else:
        raise ValueError('Unknown workflow stage type {}'.format(stage_type))

    return compose_file


def render_compose_template(template, **kwargs):
    """Render a docker compose template."""
    template = jinja2.Template(template)
    return template.render(kwargs)
