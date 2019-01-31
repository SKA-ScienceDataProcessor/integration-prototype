# -*- coding: utf-8 -*-
"""Tests of the Processing Block API.

The Processing Block API is used for interacting with individual
Processing Blocks in the Configuration database.
"""
import datetime
import os

from .utils import add_mock_sbi_workflow_definitions
from .. import ProcessingBlock, SchedulingBlockInstance, workflow_definition
from ... import ConfigDb
from ...utils.generate_sbi_config import generate_sbi_config

DB = ConfigDb()


def test_pb_properties():
    """Test accessor methods on the PB object."""
    DB.flush_db()

    # Generate a SBI configuration structure
    sbi_config = generate_sbi_config(register_workflows=True)

    # Create reference to the PB data structure in the SBI
    pb_config = sbi_config['processing_blocks'][0]

    # Delete the PB priority, if missing the PB will be created with
    # priority == 0
    del pb_config['priority']

    # Create the SBI object in the database
    sbi = SchedulingBlockInstance.from_config(sbi_config)

    # Query the list of PB ids in the database.
    pb_ids = sbi.processing_block_ids
    assert len(pb_ids) == 1

    # Obtain a PB data object from the PB identifier
    pb = ProcessingBlock(pb_ids[0])

    # Test PB accessor methods
    assert pb.id == pb_ids[0]
    assert pb.version == '2.0'
    assert pb.sbi_id == sbi.id
    assert pb.type in ('realtime', 'offline')
    assert pb.status == 'created'
    assert pb.created <= datetime.datetime.utcnow()
    assert pb.updated <= datetime.datetime.utcnow()
    assert pb.priority == 0
    assert not pb.dependencies
    assert pb.workflow_id == pb_config['workflow']['id']
    assert pb.workflow_version == pb_config['workflow']['version']
    assert not pb.workflow_stages
    assert not pb.workflow_parameters
    assert isinstance(pb.config, dict)


def test_pb_workflow_config():
    """Test accessor methods for PB workflow configuration"""
    DB.flush_db()

    # Generate an SBI configuration.
    workflow_config = dict(
        id='simple-3-stage',
        version='1.0.0',
        parameters=dict(duration=10,
                        stage1=dict(duration=5, num_channels=10)))

    workflow_path = os.path.join(os.path.dirname(__file__),
                                 'workflows_v2.0', 'simple-3-stage.yaml')
    workflow_definition.load(workflow_path)
    sbi_config = generate_sbi_config(workflow_config=workflow_config,
                                     pb_config=dict(type='offline'),
                                     register_workflows=False)

    # print()
    # print(json.dumps(sbi_config, indent=2))

    # Add the SBI to the database.
    sbi = SchedulingBlockInstance.from_config(sbi_config)

    # Obtain a PB data object.
    pb_ids = sbi.processing_block_ids
    assert len(pb_ids) == 1
    pb = ProcessingBlock(pb_ids[0])

    # Obtain the workflow stage data object for the PB.
    assert pb.workflow_id == workflow_config['id']
    assert pb.workflow_version == workflow_config['version']
    assert pb.workflow_parameters == workflow_config['parameters']
    workflow_stages = pb.workflow_stages
    assert workflow_stages

    stage = workflow_stages[0]

    expected_keys = ['id', 'version', 'type', 'timeout',
                     'parameters', 'compose_file', 'args',
                     'resources_required', 'resources_assigned',
                     'updated']
    assert all(key in stage.config.keys() for key in expected_keys)
    assert stage.pb_id == pb.id
    assert stage.id == 'stage1'
    assert stage.version == '1.0.0'
    assert stage.index == 0
    assert stage.type == 'setup'
    assert stage.status == 'created'
    assert stage.timeout == '60s'
    assert stage.resources_required
    assert isinstance(stage.resources_required, list)
    assert stage.resources_required[0]['type'] == 'cpu'
    assert stage.resources_required[0]['value'] == 0.1
    assert stage.resources_required[1]['type'] == 'memory'
    assert stage.resources_required[1]['value'] == '100M'
    assert not stage.resources_assigned
    assert stage.updated <= datetime.datetime.utcnow()
    assert stage.parameters
    assert isinstance(stage.parameters, dict)
    assert stage.parameters['num_channels'] == 10
    assert stage.parameters['duration'] == 5
    # FIXME(BMo) validation of parameters against those \
    # required for the stage!?
    assert not stage.dependencies
    assert stage.args
    assert isinstance(stage.args, str)
    assert stage.compose_file
    assert isinstance(stage.compose_file, str)
    stage.status = 'running'
    assert stage.status == 'running'
    assert isinstance(repr(stage), str)
    assert '"id": "stage1"' in repr(stage)

    # # --- Example use of templates:
    # # --- Generating a compose file which can be used to run the workflow.
    # args_template = jinja2.Template(stage.args_template)
    # args_str = args_template.render(stage=stage.config,
    #                                 **pb.workflow_parameters)
    # args_str = json.dumps(json.loads(args_str))
    # assert isinstance(stage.ee_config, dict)
    # assert stage.compose_template
    # compose_template = jinja2.Template(stage.compose_template)
    # compose_str = compose_template.render(stage=dict(args=args_str))
    # assert 'services' in compose_str
    # # print()
    # # print('-------------')
    # # print(compose_str)
    # assert yaml.load(compose_str)
    #
    # stage = workflow_stages[1]
    # assert stage.id == 'processing'
    # assert stage.pb_id == pb.id
    # assert stage.index == 1
    #
    # stage = workflow_stages[2]
    # assert stage.id == 'cleanup'
    # assert stage.index == 2


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
                                     workflow_config=workflow_config,
                                     register_workflows=True)

    # Add the SBI to the database.
    sbi = SchedulingBlockInstance.from_config(sbi_config)

    pb_ids = sbi.processing_block_ids
    assert len(pb_ids) == 1

    pb = ProcessingBlock(pb_ids[0])

    assert len(pb.dependencies) == 1
    dependency0 = pb.dependencies[0]
    assert dependency0.type == pb_config['dependencies'][0]['type']
    assert dependency0.value == pb_config['dependencies'][0]['value']
    assert dependency0.condition == pb_config['dependencies'][0]['condition']


def test_pb_events():
    """Test event methods associated with the PB."""
    DB.flush_db()
    sbi_config = generate_sbi_config(num_pbs=1)
    add_mock_sbi_workflow_definitions(sbi_config)

    # Add the SBI to the database.
    sbi = SchedulingBlockInstance.from_config(sbi_config)

    pb_ids = sbi.processing_block_ids
    assert len(pb_ids) == 1

    pb = ProcessingBlock(pb_ids[0])
    events = pb.subscribe('test_subscriber')
    assert not events.get_published_events()
    assert len(pb.get_subscribers()) == 1
    assert pb.get_subscribers()[0] == 'test_subscriber'
