# -*- coding: utf-8 -*-
"""Unit tests of the Scheduling Block Instance resource provided by the PCI"""
import json
from http import HTTPStatus
import pytest


@pytest.mark.usefixtures("app", "root_url")
def test_get_scheduling_block_list(app, root_url):
    """Test GET of the scheduling block instance list"""
    response = app.get(root_url + 'scheduling-blocks')
    assert response.mimetype == 'application/json'
    assert response.status_code == HTTPStatus.OK
    data = json.loads(response.get_data())
    assert 'scheduling_blocks' in data
    assert 'links' in data
    assert len(data['scheduling_blocks']) == 10


@pytest.mark.usefixtures("app", "root_url", "db_client")
def test_get_scheduling_block_detail(app, root_url, db_client):
    """Test GET details of a scheduling block"""
    sbi_ids = db_client.get_sched_block_instance_ids()
    assert sbi_ids
    sbi_id = db_client.get_sched_block_instance_ids()[0]
    response = app.get(root_url + 'scheduling-block/' + sbi_id)
    assert response.mimetype == 'application/json'
    assert response.status_code == HTTPStatus.OK
    data = json.loads(response.get_data())
    assert 'id' in data
    assert 'sub_array_id'
    assert 'links' in data
    assert 'status' in data
    assert 'processing_blocks' in data


@pytest.mark.usefixtures("app", "root_url")
def test_post_valid_sbi(app, root_url):
    """Test POSTing a SBI to the SBI list."""
    config = dict(id='00000000-sip-sbi999',
                  sub_array_id='subarray-00',
                  sched_block_id='00000000-sip-sb000',
                  processing_blocks=[])
    config = json.dumps(config)
    response = app.post(root_url + 'scheduling-blocks',
                        data=config, content_type='application/json')
    assert response.mimetype == 'application/json'
    assert response.status_code == HTTPStatus.ACCEPTED
    data = json.loads(response.get_data())
    assert 'message' in data
    assert 'links' in data
    assert 'config' in data


def test_post_invalid_sbi():
    """Test POSTing an invalid SBI configuration."""


def test_successful_delete_sbi():
    """Test deleting an SBI successfully"""


@pytest.mark.usefixtures("app", "root_url")
def test_delete_sbi_error(app, root_url):
    """Test deleting an SBI that doesn't exist"""
    response = app.delete(root_url + 'scheduling-block/foo')
    assert response.mimetype == 'application/json'
    assert response.status_code == HTTPStatus.BAD_REQUEST
    data = json.loads(response.get_data())
    assert 'error' in data
