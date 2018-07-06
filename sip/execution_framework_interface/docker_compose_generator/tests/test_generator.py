# -*- coding: utf-8 -*-
"""."""
import os
import json

import yaml
import jinja2

import pytest

from ..generator import generate_compose_file, load_template


def test_generate_sender_compose_file():
    """Test generating a Docker Compose file for visibility send."""
    # Load workflow stage configuration (for the visibility sender).
    # This would normally be in the Configuraiton db and loaded by the
    # Processing Controller (Scheduler) or Processing Block Controller.
    path = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(path, 'scheduler_config.yml'), 'r') as _file:
        config = yaml.load(_file)
    assert 'scheduler_config' in config
    assert config['scheduler_config'][0]['type'] == 'vis_send'
    vis_send_config = config['scheduler_config'][0]['config']
    assert 'num_senders' in vis_send_config
    assert 'docker_compose_template' in vis_send_config
    assert 'app_config_template' in vis_send_config

    # Load the compose file template specified by the workflow configuration.
    _dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..',
                                        'example_templates'))
    template_loader = jinja2.FileSystemLoader(searchpath=_dir,
                                              followlinks=True)
    template_env = jinja2.Environment(loader=template_loader)
    path = vis_send_config['docker_compose_template']
    compose_template = template_env.get_template(path)

    # Load the application template specified by the workflow configuration.
    path = vis_send_config['app_config_template']
    app_config_template = template_env.get_template(path)

    senders = []
    for i in range(vis_send_config['num_senders']):
        app_config = app_config_template.render(
            destination_host=vis_send_config['destination_hosts'][i],
            destination_port_start='41000'
        )
        app_config = json.loads(app_config)
        senders.append(dict(id='{:02d}'.format(i),
                            service_name='sender{:02d}'.format(i),
                            config=json.dumps(app_config)))

    compose_file = compose_template.render(senders=senders)

    compose_dict = yaml.load(compose_file)
    assert compose_dict['version'] == '3.6'
    assert 'services' in compose_dict
    assert 'sender00' in compose_dict['services']
    assert 'sender01' in compose_dict['services']

    # Will not need to write the file if passing the file
    # as a string to the Docker Swarm EE interface.
    # with open('test_send.yml', 'w') as _file:
    #     _file.write(compose_file)


def test_generate_receiver_compose_file():
    """Test generating a Docker Compose file for visibility receive."""
    # Load workflow stage configuration (for the visibility sender).
    # This would normally be in the Configuraiton db and loaded by the
    # Processing Controller (Scheduler) or Processing Block Controller.
    path = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(path, 'scheduler_config.yml'), 'r') as _file:
        config = yaml.load(_file)
    assert 'scheduler_config' in config
    assert config['scheduler_config'][1]['type'] == 'vis_recv'
    vis_recv_config = config['scheduler_config'][1]['config']
    assert 'num_receivers' in vis_recv_config
    assert 'docker_compose_template' in vis_recv_config
    assert 'app_config' in vis_recv_config

    # Load the compose file template.
    _dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..',
                                        'example_templates'))
    template_loader = jinja2.FileSystemLoader(searchpath=_dir,
                                              followlinks=True)
    template_env = jinja2.Environment(loader=template_loader)
    path = vis_recv_config['docker_compose_template']
    compose_template = template_env.get_template(path)

    # Load application configuration.
    path = vis_recv_config['app_config']
    with open(os.path.join(_dir, path)) as _file:
        app_config = json.load(_file)

    # Render the compose file template.
    template_params = dict(json_config=app_config,
                           buffer_path=vis_recv_config['buffer_path'],
                           num_receivers=vis_recv_config['num_receivers'])
    compose_file = compose_template.render(**template_params)

    # Verify the template was rendered correctly.
    compose_dict = yaml.load(compose_file)
    assert compose_dict['version'] == '3.6'
    assert 'services' in compose_dict
    assert 'recv' in compose_dict['services']
    assert 'networks' in compose_dict

    # Will not need to write the file if passing the file
    # as a string to the Docker Swarm EE interface.
    # with open('test_recv.yml', 'w') as _file:
    #     _file.write(compose_file)


def test_generate_compose_file_invalid_config():
    """."""
    with pytest.raises(RuntimeError):
        _ = generate_compose_file(dict())


def test_load_template():
    """."""
    template = load_template('docker-compose.recv.j2.yml')
    assert isinstance(template, jinja2.Template)
    assert os.path.isfile(template.filename)
    # print(vars(template.module))
    # print(template.module.version)

    with pytest.raises(jinja2.exceptions.TemplateNotFound):
        _ = load_template('does_not_exist.j2')


def test_generate_sender_compose_file_2():
    """Test generating a Docker Compose file for visibility send."""
    path = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(path, 'scheduler_config.yml'), 'r') as _file:
        config = yaml.load(_file)
    config = config['scheduler_config'][0]['config']

    # config = {}
    compose_file = generate_compose_file(config)
    print(compose_file)
