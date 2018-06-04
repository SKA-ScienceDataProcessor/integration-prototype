# -*- coding: utf-8 -*-
"""Unit tests for the Master Controller REST variant.

- http://flask.pocoo.org/docs/0.12/testing/
"""
import json
from http import HTTPStatus

from ..app import APP
from ..db.client import ConfigDb
from ..db.init import add_scheduling_blocks


DB = ConfigDb()
API_URL = '/api/v1/'
add_scheduling_blocks(10, clear=True)
assert len(DB.get_sched_block_instance_ids()) == 10


APP.config['TESTING'] = True
APP.config['DEBUG'] = False
APP.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
assert APP.debug is False
FLASK_APP = APP.test_client()


def test_invalid_url():
    """Test requesting an invalid URL"""
    # TODO


def test_get_root():
    """Test GET of the root URL."""
    response = FLASK_APP.get('/')
    assert response.mimetype == 'application/json'
    assert response.status_code == HTTPStatus.OK
    data = json.loads(response.get_data())
    assert 'links' in data


def test_health():
    """Test the health URL"""
    response = FLASK_APP.get(API_URL + 'health')
    assert response.mimetype == 'application/json'
    assert response.status_code == HTTPStatus.OK
    data = json.loads(response.get_data())
    assert 'state' in data
    assert 'uptime' in data


def test_get_scheduling_block_list():
    """Test GET of the scheduling block instance list"""
    response = FLASK_APP.get(API_URL + 'scheduling-blocks')
    assert response.mimetype == 'application/json'
    assert response.status_code == HTTPStatus.OK
    data = json.loads(response.get_data())
    assert 'scheduling_blocks' in data
    assert 'links' in data
    assert len(data['scheduling_blocks']) == 10


def test_get_processing_block_list():
    """Test GET of the processing block list"""
    response = FLASK_APP.get(API_URL + 'processing-blocks')
    assert response.mimetype == 'application/json'
    assert response.status_code == HTTPStatus.OK
    data = json.loads(response.get_data())
    assert 'processing_blocks' in data
    assert 'links' in data


def test_get_subarrays_list():
    """Test GET of the subarray list"""
    response = FLASK_APP.get(API_URL + 'sub-arrays')
    assert response.mimetype == 'application/json'
    assert response.status_code == HTTPStatus.OK
    data = json.loads(response.get_data())
    assert 'sub_arrays' in data
    assert 'links' in data


def test_get_scheduling_block_detail():
    """Test GET details of a scheduling block"""
    sbi_id = DB.get_sched_block_instance_ids()[0]
    response = FLASK_APP.get(API_URL + 'scheduling-block/' + sbi_id)
    assert response.mimetype == 'application/json'
    assert response.status_code == HTTPStatus.OK
    data = json.loads(response.get_data())
    assert 'id' in data
    assert 'sub_array_id'
    assert 'links' in data
    assert 'status' in data
    assert 'processing_blocks' in data


def test_get_processing_block_detail():
    """Test GET details of a processing block"""
    pb_id = DB.get_processing_block_ids()[0]
    response = FLASK_APP.get(API_URL + 'processing-block/' + pb_id)
    assert response.mimetype == 'application/json'
    assert response.status_code == HTTPStatus.OK
    data = json.loads(response.get_data())
    assert 'id' in data
    assert 'links' in data
    assert 'workflow' in data


def test_get_valid_subarray_detail():
    """Test GET details of given subarray that exists

    This should list the SBIs associated with the subarray
    """
    sub_array_id = DB.get_sub_array_ids()[0]
    response = FLASK_APP.get(API_URL + 'sub-array/' + sub_array_id)
    data = json.loads(response.get_data())
    assert response.mimetype == 'application/json'
    assert response.status_code == HTTPStatus.OK
    assert 'scheduling_blocks' in data
    assert 'links' in data


def test_get_invalid_subarray_detail():
    """Test GET details of given subarray that doesnt exist

    This should list the SBIs associated with the subarray
    """
    response = FLASK_APP.get(API_URL + 'sub-array/' + 'foo')
    data = json.loads(response.get_data())
    assert response.mimetype == 'application/json'
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert 'error' in data
    assert 'Invalid sub-array ID' in data['error']

    # This test only works as the generator does not generate any SBIs
    # in subarray-15
    response = FLASK_APP.get(API_URL + 'sub-array/' + 'subarray-15')
    data = json.loads(response.get_data())
    assert response.mimetype == 'application/json'
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert 'error' in data
    assert 'does not currently exist' in data['error']


def test_post_valid_sbi():
    """Test POSTing a SBI to the SBI list."""
    config = dict(id='00000000-sip-sbi999',
                  sub_array_id='subarray-00',
                  sched_block_id='00000000-sip-sb000',
                  processing_blocks=[])
    config = json.dumps(config)
    response = FLASK_APP.post(API_URL + 'scheduling-blocks',
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


def test_delete_sbi_error():
    """Test deleting an SBI that doesn't exist"""
    response = FLASK_APP.delete(API_URL + 'scheduling-block/foo')
    assert response.mimetype == 'application/json'
    assert response.status_code == HTTPStatus.BAD_REQUEST
    data = json.loads(response.get_data())
    assert 'error' in data
