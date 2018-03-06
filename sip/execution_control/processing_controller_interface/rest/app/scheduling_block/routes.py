# -*- coding: utf-8 -*-
"""Scheduling blocks route"""
from flask import Blueprint, request
from flask_api import status

from ..mock_config_db_client import get_scheduling_block, \
                                    delete_scheduling_block


API = Blueprint('scheduling_block', __name__)


@API.route('/scheduling-block/<block_id>', methods=['GET'])
def get_scheduling_block_detail(block_id):
    """Scheduling block detail resource."""
    block = get_scheduling_block(block_id)
    response = block
    response['_links'] = {
        'self': '{}'.format(request.url),
        'list': '{}scheduling-blocks'.format(request.url_root)
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
