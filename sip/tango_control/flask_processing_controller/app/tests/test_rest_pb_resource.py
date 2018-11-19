# -*- coding: utf-8 -*-
"""Unit tests of the Processing Block resource(s) provided by the PCI"""
import json
from http import HTTPStatus
import pytest


@pytest.mark.usefixtures("db_client", "app", "root_url", "init_db")
def test_get_processing_block_list(db_client, app, root_url):
    """Test GET of the processing block list"""
    assert len(db_client.get_sched_block_instance_ids()) == 10
    response = app.get(root_url + 'processing-blocks')
    assert response.mimetype == 'application/json'
    assert response.status_code == HTTPStatus.OK
    data = json.loads(response.get_data())
    assert 'processing_blocks' in data
    assert 'links' in data


@pytest.mark.usefixtures("db_client", "app", "root_url", "init_db")
def test_get_valid_pb_detail(db_client, app, root_url):
    """Test GET details of a processing block"""
    assert len(db_client.get_sched_block_instance_ids()) == 10
    pb_id = db_client.get_processing_block_ids()[0]
    response = app.get(root_url + 'processing-block/' + pb_id)
    assert response.mimetype == 'application/json'
    assert response.status_code == HTTPStatus.OK
    data = json.loads(response.get_data())
    assert 'id' in data
    assert 'links' in data
    assert 'workflow' in data


@pytest.mark.usefixtures("db_client", "app", "root_url", "init_db")
def test_get_invalid_pb_detail(db_client, app, root_url):
    """Test GET details of a processing block with an invalid id"""
    assert len(db_client.get_sched_block_instance_ids()) == 10
    response = app.get(root_url + 'processing-block/' + 'foo')
    assert response.mimetype == 'application/json'
    assert response.status_code == HTTPStatus.NOT_FOUND
    data = json.loads(response.get_data())
    assert 'error' in data
    assert 'links' in data


@pytest.mark.usefixtures("db_client", "app", "root_url", "init_db")
def test_delete_valid_pb(db_client, app, root_url):
    """Test DELETE of a Processing Block"""
    assert len(db_client.get_sched_block_instance_ids()) == 10
    pb_id = db_client.get_processing_block_ids()[0]
    num_pbs = len(db_client.get_processing_block_ids())
    response = app.delete(root_url + 'processing-block/' + pb_id)
    assert response.mimetype == 'application/json'
    assert response.status_code == HTTPStatus.OK
    data = json.loads(response.get_data())
    assert 'message' in data
    assert 'Deleted block' in data['message']
    assert len(db_client.get_processing_block_ids()) == num_pbs - 1


@pytest.mark.usefixtures("app", "root_url", "db_client")
def test_delete_invalid_pb(app, root_url, db_client):
    """Test DELETE of a Processing Block with an invalid id"""
    num_pbs = len(db_client.get_processing_block_ids())
    response = app.delete(root_url + 'processing-block/' + 'foo')
    assert response.mimetype == 'application/json'
    assert response.status_code == HTTPStatus.OK
    data = json.loads(response.get_data())
    assert 'error' in data
    assert 'Failed to delete' in data['error']
    assert len(db_client.get_processing_block_ids()) == num_pbs
