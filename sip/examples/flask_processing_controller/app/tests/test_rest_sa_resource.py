# -*- coding: utf-8 -*-
"""Unit tests of the Sub-array resource(s) provided by the PCI"""
import json
from http import HTTPStatus
import pytest


@pytest.mark.usefixtures("app", "root_url")
def test_get_subarrays_list(app, root_url):
    """Test GET of the subarray list"""
    response = app.get(root_url + 'sub-arrays')
    assert response.mimetype == 'application/json'
    assert response.status_code == HTTPStatus.OK
    data = json.loads(response.get_data())
    assert 'sub_arrays' in data
    assert 'links' in data


@pytest.mark.usefixtures("app", "root_url", "db_client", "init_db")
def test_get_valid_subarray_detail(app, root_url, db_client):
    """Test GET details of given subarray that exists

    This should list the SBIs associated with the subarray
    """
    sub_array_id = db_client.get_sub_array_ids()[0]
    response = app.get(root_url + 'sub-array/' + sub_array_id)
    data = json.loads(response.get_data())
    assert response.mimetype == 'application/json'
    assert response.status_code == HTTPStatus.OK
    assert 'scheduling_blocks' in data
    assert 'links' in data


@pytest.mark.usefixtures("app", "root_url", "init_db")
def test_get_invalid_subarray_detail(app, root_url):
    """Test GET details of given subarray that doesnt exist

    This should list the SBIs associated with the subarray
    """
    response = app.get(root_url + 'sub-array/' + 'foo')
    data = json.loads(response.get_data())
    assert response.mimetype == 'application/json'
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert 'error' in data
    assert 'Invalid sub-array ID' in data['error']

    # This test only works as the generator does not generate any SBIs
    # in subarray-15
    response = app.get(root_url + 'sub-array/' + 'subarray-15')
    data = json.loads(response.get_data())
    assert response.mimetype == 'application/json'
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert 'error' in data
    assert 'does not currently exist' in data['error']
