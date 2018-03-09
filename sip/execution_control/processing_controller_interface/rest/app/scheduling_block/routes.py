# -*- coding: utf-8 -*-
"""Scheduling blocks route"""
from flask import Blueprint, request
from flask_api import status

from ..mock_config_db_client import get_scheduling_block, \
                                    get_scheduling_block_ids, \
                                    delete_scheduling_block


API = Blueprint('scheduling_block', __name__)


@API.route('/scheduling-block/<block_id>', methods=['GET'])
def get_scheduling_block_detail(block_id):
    """Scheduling block detail resource."""
    blocks = get_scheduling_block_ids()
    block = get_scheduling_block(block_id)
    this_index = blocks.index(block_id)
    next_index = this_index + 1 if this_index + 1 < len(blocks) else 0
    prev_index = this_index - 1 if this_index - 1 > 0 else len(blocks) - 1
    response = block
    response['links'] = {
        'self': '{}'.format(request.url),
        'next': '{}scheduling-block/{}'.format(request.url_root,
                                               blocks[next_index]),
        'prev': '{}scheduling-block/{}'.format(request.url_root,
                                               blocks[prev_index]),
        'list': '{}scheduling-blocks'.format(request.url_root),
        'home': '{}'.format(request.url_root)
    }
    return block


@API.route('/scheduling-block/<block_id>', methods=['DELETE'])
def delete_scheduling_block_request(block_id):
    """Scheduling block detail resource."""
    try:
        delete_scheduling_block(block_id)
        response = dict(message='Deleted block: _id = {}'.format(block_id))
        response['_links'] = {
            'list': '{}scheduling-blocks'.format(request.url_root)
        }
        return response, status.HTTP_200_OK
    except:  # TODO(BM) handle specific exceptions for blocks not existing etc.
        return {'error': 'Unable to delete block.'}, \
            status.HTTP_400_BAD_REQUEST
