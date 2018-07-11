# -*- coding: utf-8 -*-
"""."""
import os
import logging

import yaml
import jinja2

import pytest

from ..compose_generator import generate_compose_file
from ..generators.utils import load_template


logging.basicConfig(level='DEBUG')


def test_generate_compose_file_invalid_config():
    """Generate a compose file with invalid configuration.

    This should raise an exeception.
    """
    with pytest.raises(RuntimeError):
        _ = generate_compose_file(dict())


def test_load_template():
    """Try to load a jinja template using the load_template utility method.

    If the file exits this should work correctly, otherwise an exception
    should be raised.
    """
    template = load_template('docker-compose.recv.j2.yml')
    assert isinstance(template, jinja2.Template)
    assert os.path.isfile(template.filename)

    with pytest.raises(jinja2.exceptions.TemplateNotFound):
        _ = load_template('does_not_exist.j2')


def test_generate_csp_vis_emualator():
    """Test generating a Docker Compose file for visibility send.

    This should result in a correctly formed compose file.
    """
    # Obtain workflow stage configuration
    path = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(path, 'workflow_stage_config.yml'), 'r') as _file:
        config = yaml.load(_file)

    # Generate and verify the compose file
    stage_index = 1
    assert config['workflow'][stage_index]['type'] == 'csp_vis_emulator'
    compose_file = generate_compose_file(config['workflow'][stage_index])
    compose_dict = yaml.load(compose_file)
    assert 'services' in compose_dict
    assert 'networks' in compose_dict
    assert 'version' in compose_dict
    assert 'sender000' in compose_dict['services']
    assert 'sender001' in compose_dict['services']


def test_generate_vis_ingest():
    """Test generating a Docker Compose file for visibility ingest.

    This should result in a correctly formed compose file.
    """
    # Obtain workflow stage configuration
    path = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(path, 'workflow_stage_config.yml'), 'r') as _file:
        config = yaml.load(_file)

    # Generate and verify the compose file
    stage_index = 2
    assert config['workflow'][stage_index]['type'] == 'vis_ingest'
    compose_file = generate_compose_file(config['workflow'][stage_index])
    compose_dict = yaml.load(compose_file)
    assert 'services' in compose_dict
    assert 'networks' in compose_dict
    assert 'version' in compose_dict
    assert 'recv' in compose_dict['services']
    assert compose_dict['services']['recv']['deploy']['replicas'] == 2
