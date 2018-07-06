# -*- coding: utf-8 -*-
"""."""
import os

import jinja2


def load_template(file_path, search_paths=None):
    """Load a Jinja2 template.

    Args:
        file_path (str): Path of the template file to be loaded. This path
                         should be relative to a path specified in the
                         search_paths list.
        search_paths (list, optional): List of search paths where templates
                                       are located.

    Returns:
        (jinja2.Template) Jinja2 template object.

    """
    if not search_paths:
        _cwd = os.path.abspath(os.path.dirname(__file__))
        _dir = os.path.join(_cwd, 'example_templates')
        search_paths = _dir

    _loader = jinja2.FileSystemLoader(searchpath=search_paths)
    _env = jinja2.Environment(loader=_loader)
    return _env.get_template(file_path)


def generate_compose_file(workflow_stage_config):
    """Dynamically generate Docker compose file.

    This convers workflow stage configuration, stored in the Configuration
    Database, into a Docker Compose file string that can be used to execture
    a workflow stage.
    """
    if 'docker_compose_template' not in workflow_stage_config:
        raise RuntimeError('Docker Compose template not found in '
                           'configuration')

    # _cwd = os.path.join(os.path.dirname(__file__))
    # _dir = os.path.abspath(_cwd, 'example_templates')
    # template_loader

    return ''


def render_compose_template(template, **kwargs):
    """Render a docker compose template."""
    template = jinja2.Template(template)
    return template.render(kwargs)
