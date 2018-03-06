# -*- coding: utf-8 -*-
"""Scheduling blocks route"""
from flask import Blueprint, request
from flask_api import status
import jsonschema

from ..mock_config_db_client import get_scheduling_block_ids, \
                                    get_scheduling_block, \
                                    add_scheduling_block


API = Blueprint('scheduling_block_list', __name__)


@API.route('/scheduling-blocks', methods=['GET'])
def get_scheduling_block_list():
    """Return the list of Scheduling Blocks instances known to SDP."""
    response = dict(scheduling_blocks=[],
                    links=dict(home="{}".format(request.url_root)))
    blocks = response['scheduling_blocks']
    block_ids = get_scheduling_block_ids()

    for block_id in block_ids:
        block = get_scheduling_block(block_id)
        # Remove processing blocks key.
        # Scheduling blocks list should just be a summary.
        print(block['processing_blocks'])
        print(type(block['processing_blocks']))
        block['num_processing_blocks'] = len(block['processing_blocks'])
        try:
            del block['processing_blocks']
        except KeyError:
            pass
        block['links'] = {
            'self': '{}scheduling-block/{}'.format(request.url_root,
                                                   block_id)
        }
        blocks.append(block)
    return response, status.HTTP_200_OK


@API.route('/scheduling-blocks', methods=['POST'])
def create_scheduling_block():
    """Create / register a Scheduling Block instance with SDP."""
    config = request.data
    try:
        add_scheduling_block(config)
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
