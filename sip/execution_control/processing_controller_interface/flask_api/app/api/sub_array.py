# -*- coding: utf-8 -*-
"""Sub array route"""
import os
from random import choice

import jsonschema
from flask import Blueprint, request, abort
from http import HTTPStatus

from .utils import get_root_url
from ..db.client import ConfigDbClient

BP = Blueprint('sub-array', __name__)
DB = ConfigDbClient()


@BP.route('/sub-array/<sub_array_id>', methods=['GET'])
def _get(sub_array_id):
    """Sub array detail resource.

    This method will list scheduling blocks and processing blocks
    in the specified sub-array.
    """
    block_ids = DB.get_sub_array_scheduling_block_ids(sub_array_id)
    _blocks = [b for b in DB.get_block_details(block_ids)]
    response = dict(scheduling_blocks=[])
    _url = get_root_url()
    for block in _blocks:
        block['links'] = {
            'self': '{}/scheduling-block/{}'.format(_url, block['id'])
        }
        response['scheduling_blocks'].append(block)
    response['links'] = {
        'self': '{}'.format(request.url),
        'list': '{}/sub-arrays'.format(_url),
        'home': '{}'.format(_url),
    }
    return response, HTTPStatus.OK


@BP.route('/sub-array/<sub_array_id>', methods=['POST'])
def _create(sub_array_id):
    """Create / register a Scheduling Block instance with SDP."""
    config = request.data
    config['sub_array_id'] = 'subarray-{:02d}'.format(sub_array_id)
    # schema_path = os.path.dirname(os.path.abspath(__file__))
    # schema_path = os.path.join(schema_path, 'post_request.json')
    try:
        # add_scheduling_block(config, schema_path)
        DB.set_scheduling_block(config)
    except jsonschema.ValidationError as error:
        error_dict = error.__dict__
        for key in error_dict:
            error_dict[key] = error_dict[key].__str__()
        error_response = dict(message="Failed to add scheduling block",
                              reason="JSON validation error",
                              details=error_dict)
        return error_response, HTTPStatus.BAD_REQUEST
    response = config
    response['links'] = {
        'self': '{}scheduling-block/{}'.format(request.url_root,
                                               config['id']),
        'next': 'TODO',
        'previous': 'TODO',
        'list': '{}'.format(request.url),
        'home': '{}'.format(request.url_root)
    }
    response = []
    return response, HTTPStatus.ACCEPTED


@BP.route('/sub-array/<sub_array_id>/status', methods=['GET'])
def _get_status(sub_array_id):
    """Return the status of the sub-array"""
    # TODO(BM) Implement this properly
    return dict(sub_array_id=sub_array_id,
                status=choice(['OK', 'INACTIVE'])), HTTPStatus.OK


@BP.route('/sub-array/<sub_array_id>/scheduling-blocks', methods=['GET'])
def _get_scheduling_blocks(sub_array_id):
    """Return the list of scheduling blocks instances associated with the sub
    array"""
    block_ids = DB.get_sub_array_scheduling_block_ids(sub_array_id)
    return block_ids, HTTPStatus.OK


@BP.route('/sub-array/<sub_array_id>/scheduling-block/<block_id>',
          methods=['GET'])
def _get_scheduling_block(sub_array_id, block_id):
    """Return the list of scheduling blocks instances associated with the sub
    array"""
    block_ids = DB.get_sub_array_scheduling_block_ids(sub_array_id)
    if block_id in block_ids:
        block = DB.get_block_details([block_id]).__next__()
        return block, HTTPStatus.OK
    else:
        abort(HTTPStatus.NOT_FOUND)



