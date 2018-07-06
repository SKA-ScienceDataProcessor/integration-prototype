# -*- coding: utf-8 -*-
"""."""
import os
import json

import yaml
import jinja2

# from ..generator import render_compose_template


def test_generate_sender_compose_file():
    """Test generating a Docker Compose file for visibility send."""
    # - Load mock scheduler configuration for the visibility sender.
    # - Workflow stage configuration would normally be in the Configuraiton db
    #   and loaded by the Processing Controller (Scheduler) or
    #   Processing Block Controller.
    path = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(path, 'scheduler_config.yml'), 'r') as _file:
        config = yaml.load(_file)
    print(config)
    assert 'scheduler_config' in config
    assert config['scheduler_config'][0]['type'] == 'vis_send'
    vis_send_config = config['scheduler_config'][0]['config']
    assert 'num_senders' in vis_send_config
    assert 'docker_compose_template' in vis_send_config
    assert 'app_config_template' in vis_send_config

    _dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..',
                                        'example_templates'))
    template_loader = jinja2.FileSystemLoader(searchpath=_dir,
                                              followlinks=True)
    template_env = jinja2.Environment(loader=template_loader)
    path = vis_send_config['docker_compose_template']
    compose_template = template_env.get_template(path)

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
    path = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(path, 'scheduler_config.yml'), 'r') as _file:
        config = yaml.load(_file)
    assert 'scheduler_config' in config
    assert config['scheduler_config'][1]['type'] == 'vis_recv'
    vis_recv_config = config['scheduler_config'][1]['config']
    assert 'num_receivers' in vis_recv_config
    assert 'docker_compose_template' in vis_recv_config
    assert 'app_config' in vis_recv_config

    _dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..',
                                        'example_templates'))
    template_loader = jinja2.FileSystemLoader(searchpath=_dir,
                                              followlinks=True)
    template_env = jinja2.Environment(loader=template_loader)
    path = vis_recv_config['docker_compose_template']
    compose_template = template_env.get_template(path)

    path = vis_recv_config['app_config']
    with open(os.path.join(_dir, path)) as _file:
        app_config = json.load(_file)

    template_params = dict(json_config=app_config,
                           buffer_path=vis_recv_config['buffer_path'],
                           num_receivers=vis_recv_config['num_receivers'])
    compose_file = compose_template.render(**template_params)

    compose_dict = yaml.load(compose_file)
    assert compose_dict['version'] == '3.6'
    assert 'services' in compose_dict
    assert 'recv' in compose_dict['services']
    assert 'networks' in compose_dict

    # Will not need to write the file if passing the file
    # as a string to the Docker Swarm EE interface.
    # with open('test_recv.yml', 'w') as _file:
    #     _file.write(compose_file)
