# coding=utf-8
"""Unit tests of the workflow definition interface."""
from os.path import dirname, join

import jsonschema
import pytest

from .utils import add_mock_workflow_definition
from .. import workflow_definition
from ... import ConfigDb

DB = ConfigDb()


def test_workflow_definition_load_fail(tmp_path):
    """Test fail conditions loading a workflow definition"""
    DB.flush_db()
    # Loading a file that does not exist results in a useful error
    with pytest.raises(ValueError,
                       match=r'^Specified workflow path does not exist'):
        workflow_definition.load('foo')

    # Loading a workflow file with a missing 'stages' directory results
    # in a useful error.
    temp_directory = tmp_path / "workflows"
    temp_directory.mkdir()
    temp_workflow_file = temp_directory / "foo.json"
    temp_workflow_file.write_text("{}")
    with pytest.raises(ValueError, match=r'Stages directory does not exist!'):
        workflow_definition.load(str(temp_workflow_file))

    # Loading a file with an invalid extension results in a useful error
    temp_stages_directory = temp_directory / "stages"
    temp_stages_directory.mkdir()
    temp_workflow_file = temp_directory / "foo.txt"
    temp_workflow_file.write_text("{}")
    with pytest.raises(ValueError, match=r'^Unexpected file extension.'):
        workflow_definition.load(str(temp_workflow_file))

    # Loading a workflow where the docker-compose file in the stage is missing
    workflows_dir = join(dirname(__file__), 'workflows_v2.0')
    with pytest.raises(FileNotFoundError,
                       match=r'Workflow stage Docker compose file missing!'):
        workflow_definition.load(join(workflows_dir, 'no-compose-file.json'))

    # Loading a workflow with a stage with invalid args file
    workflows_dir = join(dirname(__file__), 'workflows_v2.0')
    with pytest.raises(FileNotFoundError, match=r'Expecting args file'):
        workflow_definition.load(join(workflows_dir,
                                      'invalid-args-file.json'))

    # Loading a workflow with a stage with invalid parameters file
    workflows_dir = join(dirname(__file__), 'workflows_v2.0')
    with pytest.raises(FileNotFoundError, match=r'Expecting parameters file'):
        workflow_definition.load(join(workflows_dir,
                                      'invalid-parameters-file.json'))


def test_workflow_definition_load():
    """Test loading and registering (adding) workflow definitions."""
    DB.flush_db()

    workflows_dir = join(dirname(__file__), 'workflows_v2.0')

    filenames = [
        'ingest-test-01.yaml.j2',
        'simple-3-stage.yaml',
        'simple-1-stage.json'
    ]

    try:
        for filename in filenames:
            workflow_definition.load(join(workflows_dir, filename))
    except jsonschema.ValidationError:
        pytest.fail('Unexpected schema validation error')

    workflows = workflow_definition.get_workflows()
    assert len(workflows) == 3

    # Loading a workflow that already exists results in a KeyError exception
    with pytest.raises(KeyError, match=r'Workflow definition already exists:'):
        workflow_definition.load(join(workflows_dir, filenames[0]))


def test_workflow_definitions_get():
    """Test retrieving workflow definitions."""
    DB.flush_db()

    workflows = workflow_definition.get_workflows()
    assert not workflows

    add_mock_workflow_definition('my_workflow', '1.0.0')
    add_mock_workflow_definition('my_workflow', '1.5.0')
    add_mock_workflow_definition('my_workflow', '2.5.0')
    add_mock_workflow_definition('my_workflow', 'test')

    workflows = workflow_definition.get_workflows()
    assert 'my_workflow' in workflows
    assert len(workflows['my_workflow']) == 4
    assert '1.0.0' in workflows['my_workflow']

    workflow = workflow_definition.get_workflow('my_workflow', '1.0.0')
    assert 'id' in workflow
    assert workflow['id'] == 'my_workflow'
    assert workflow['version'] == '1.0.0'

    with pytest.raises(KeyError, match=r'not found!'):
        workflow_definition.get_workflow('foo', '1.0.0')
