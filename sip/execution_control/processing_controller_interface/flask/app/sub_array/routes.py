# -*- coding: utf-8 -*-
"""Sub array route"""
import os
from flask import Blueprint, request
from flask_api import status
import jsonschema

from ..mock_config_db_client import get_sub_array_scheduling_block_ids, \
                                    get_scheduling_block, \
                                    add_scheduling_block


API = Blueprint('sub_array_api', __name__)


@API.route('/sub-array/<sub_array_id>', methods=['GET'])
def get_sub_array_detail(sub_array_id):
    """Sub array detail resource.

    This method will list scheduling blocks and processing blocks
    in the specified sub-array.
    """
    block_ids = get_sub_array_scheduling_block_ids(sub_array_id)
    response = dict(scheduling_blocks=[])
    for block_id in block_ids:
        block = get_scheduling_block(block_id)
        block['links'] = {
            'self': '{}scheduling-block/{}'.format(request.url_root, block_id)
        }
        response['scheduling_blocks'].append(block)
    response['links'] = {
        'home': '{}'.format(request.url_root),
        'self': '{}'.format(request.url)
    }
    return response, status.HTTP_200_OK


@API.route('/sub-array/<sub_array_id>', methods=['POST'])
def create_scheduling_block(sub_array_id):
    """Create / register a Scheduling Block instance with SDP."""
    config = request.data
    config['sub_array_id'] = sub_array_id
    schema_path = os.path.dirname(os.path.abspath(__file__))
    schema_path = os.path.join(schema_path, 'post_request.json')
    try:
        add_scheduling_block(config, schema_path)
    except jsonschema.ValidationError as error:
        error_dict = error.__dict__
        for key in error_dict:
            error_dict[key] = error_dict[key].__str__()
        error_response = dict(message="Failed to add scheduling block",
                              reason="JSON validation error",
                              details=error_dict)
        return error_response, status.HTTP_400_BAD_REQUEST
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
    return response, status.HTTP_202_ACCEPTED


@API.route('/sub-array/<sub_array_id>/status', methods=['GET'])
def get_sub_array_status(sub_array_id):
    """Return the status of the sub-array"""
    return {}, status.HTTP_501_NOT_IMPLEMENTED
