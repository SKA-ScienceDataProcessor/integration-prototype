# -*- coding: utf-8 -*-
"""."""
import os
import json

import yaml
import jinja2

# from ..generator import render_compose_template


def test_generate_sender_compose_file():
    """Test generating a Docker Compose file for visibility sender services."""
    # Load mock scheduler configuration for the visibility sender
    # Workflow stage configuration would normally be in the Configuraiton db
    # and loaded by the Processing Controller (Scheduler) or
    # Processing Block Controller.
    path = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(path, 'scheduler_config.yml'), 'r') as _file:
        config = yaml.load(_file)
    assert 'scheduler_config' in config
    vis_send_config = config['scheduler_config'][0]['config']
    assert 'num_senders' in vis_send_config
    assert 'docker_compose_template' in vis_send_config
    assert 'app_config_template' in vis_send_config

    path = vis_send_config['docker_compose_template']
    path = os.path.abspath(path)
    assert os.path.exists(path)
    with open(os.path.abspath(path), 'r') as _file:
        compose_template = jinja2.Template(_file.read())

    path = vis_send_config['app_config_template']
    path = os.path.abspath(path)
    assert os.path.exists(path)
    with open(os.path.abspath(path), 'r') as _file:
        app_config_template = jinja2.Template(_file.read())

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
    # print(compose_dict)
