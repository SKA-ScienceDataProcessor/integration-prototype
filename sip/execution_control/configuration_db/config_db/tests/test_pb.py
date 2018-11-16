# -*- coding: utf-8 -*-
"""Tests of the Processing Block API.

The Processing Block API is used for interacting with individual
Processing Blocks in the Configuration database.
"""
import datetime
import json

import jinja2
import yaml

from .workflow_test_utils import add_test_sbi_workflow_definitions
from ..pb import DB, ProcessingBlock
from ..sbi import SchedulingBlockInstance
from ..utils.generate_sbi_configuration import generate_sbi_config


def test_pb_properties():
    """Test accessor methods on the PB object."""
    DB.flush_db()
    workflow_config = dict(
        id='test_workflow',
        version='4.0.0',
        parameters=dict(setup=dict(duration=5)))
    sbi_config = generate_sbi_config(1, workflow_config=workflow_config)
    pb_config = sbi_config['processing_blocks'][0]
    add_test_sbi_workflow_definitions(sbi_config, test_version=4)

    # Add the SBI to the database.
    sbi = SchedulingBlockInstance.from_config(sbi_config)

    pb_ids = sbi.get_pb_ids()
    assert len(pb_ids) == 1

    pb = ProcessingBlock(pb_ids[0])

    assert pb.id == pb_ids[0]
    assert pb.version == '0.4.0'
    assert pb.sbi_id == sbi.id
    assert pb.type == 'realtime' or pb.type == 'offline'
    assert pb.status == 'created'
    assert pb.created <= datetime.datetime.utcnow()
    assert pb.updated <= datetime.datetime.utcnow()
    assert 0 <= pb.priority <= 10
    assert not pb.resources_assigned
    assert not pb.resources_required
    assert not pb.dependencies
    assert pb.workflow_id == pb_config['workflow']['id']
    assert pb.workflow_version == pb_config['workflow']['version']
    assert pb.workflow_parameters
    workflow_stages = pb.workflow_stages
    assert len(workflow_stages) == 3


def test_pb_workflow_stage_config():
    """Test accessor methods for PB workflow stage config"""
    DB.flush_db()
    workflow_config = dict(
        id='test_workflow',
        version='4.0.0',
        parameters=dict(setup=dict(duration=5, num_channels=10)))
    sbi_config = generate_sbi_config(1, workflow_config=workflow_config,
                                     pb_config=dict(type='offline'))
    add_test_sbi_workflow_definitions(sbi_config, test_version=4)

    # Add the SBI to the database.
    sbi = SchedulingBlockInstance.from_config(sbi_config)

    pb_ids = sbi.get_pb_ids()
    assert len(pb_ids) == 1

    pb = ProcessingBlock(pb_ids[0])

    workflow_stages = pb.workflow_stages

    stage = workflow_stages[0]
    assert stage.id == 'setup'
    assert stage.pb_id == pb.id
    assert stage.index == 0
    assert stage.id in pb.workflow_parameters
    assert stage.version == 'test'
    assert stage.type == 'setup'
    assert stage.status == 'none'
    assert stage.timeout == 20
    assert not stage.dependencies
    assert not stage.resources_required
    assert not stage.resources_assigned
    assert isinstance(stage.app_config, dict)
    assert stage.args_template
    stage.status = 'started'
    assert stage.status == 'started'
    pb.update_workflow_state_status(stage.index, 'complete')
    assert stage.status == 'complete'

    # --- Example use of templates:
    # --- Generating a compose file which can be used to run the workflow.
    args_template = jinja2.Template(stage.args_template)
    args_str = args_template.render(stage=stage.config,
                                    **pb.workflow_parameters)
    args_str = json.dumps(json.loads(args_str))
    assert isinstance(stage.ee_config, dict)
    assert stage.compose_template
    compose_template = jinja2.Template(stage.compose_template)
    compose_str = compose_template.render(stage=dict(args=args_str))
    assert 'services' in compose_str
    # print()
    # print('-------------')
    # print(compose_str)
    assert yaml.load(compose_str)

    stage = workflow_stages[1]
    assert stage.id == 'processing'
    assert stage.pb_id == pb.id
    assert stage.index == 1

    stage = workflow_stages[2]
    assert stage.id == 'cleanup'
    assert stage.index == 2


def test_pb_resources():
    """Test PB / workflow resources methods."""
    DB.flush_db()
    pb_config = dict(
        resources_required=[dict(type='node', value=3,
                                 parameters=dict(flavour='compute_a',
                                                 exclusive=True))]
    )
    workflow_config = dict(
        id='test_workflow',
        version='4.0.0',
        parameters=dict(setup=dict(duration=5)))
    sbi_config = generate_sbi_config(1, pb_config=pb_config,
                                     workflow_config=workflow_config)
    add_test_sbi_workflow_definitions(sbi_config, test_version=4)

    # Add the SBI to the database.
    sbi = SchedulingBlockInstance.from_config(sbi_config)

    pb_ids = sbi.get_pb_ids()
    assert len(pb_ids) == 1

    pb = ProcessingBlock(pb_ids[0])

    assert len(pb.resources_required) == 1
    resource0 = pb.resources_required[0]
    assert resource0.type == 'node'
    assert resource0.value == 3
    assert resource0.parameters.get('flavour') == 'compute_a'
    assert resource0.parameters.get('exclusive')

    pb.add_assigned_resource('cpu', 0.1)
    pb.add_assigned_resource('memory', '2048MB')
    assert len(pb.resources_assigned) == 2
    resource0 = pb.resources_assigned[0]
    assert resource0.type == 'cpu'
    assert resource0.value == 0.1
    resource1 = pb.resources_assigned[1]
    assert resource1.type == 'memory'
    assert resource1.value == '2048MB'
    assert len(pb.resources_assigned) == 2

    # pb.remove_assigned_resource('cpu', value=0.1)
    pb.remove_assigned_resource('memory', '2048MB')
    assert len(pb.resources_assigned) == 1

    pb.clear_assigned_resources()
    assert not pb.resources_assigned


def test_pb_dependencies():
    """Test PB / workflow dependencies."""
    DB.flush_db()
    pb_config = dict(
        dependencies=[dict(type='pb',
                           value='PB-20181015-sip01',
                           condition='complete')]
    )
    workflow_config = dict(
        id='test_workflow',
        version='4.0.0',
        parameters=dict(setup=dict(duration=5)))
    sbi_config = generate_sbi_config(1, pb_config=pb_config,
                                     workflow_config=workflow_config)
    add_test_sbi_workflow_definitions(sbi_config, test_version=4)

    # Add the SBI to the database.
    sbi = SchedulingBlockInstance.from_config(sbi_config)

    pb_ids = sbi.get_pb_ids()
    assert len(pb_ids) == 1

    pb = ProcessingBlock(pb_ids[0])

    assert len(pb.dependencies) == 1
    dependency0 = pb.dependencies[0]
    assert dependency0.type == pb_config['dependencies'][0]['type']
    assert dependency0.value == pb_config['dependencies'][0]['value']
    assert dependency0.condition == pb_config['dependencies'][0]['condition']


def test_pb_methods():
    """Test PB methods (abort, add assigned resource etc.)."""
    DB.flush_db()
    sbi_config = generate_sbi_config(num_pbs=1)
    add_test_sbi_workflow_definitions(sbi_config)

    # Add the SBI to the database.
    sbi = SchedulingBlockInstance.from_config(sbi_config)

    pb_ids = sbi.get_pb_ids()
    assert len(pb_ids) == 1

    _ = ProcessingBlock(pb_ids[0])

    # FIXME(BM) finish this test...
