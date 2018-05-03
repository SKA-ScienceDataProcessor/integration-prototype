# -*- coding: utf-8 -*-
"""Scheduling block details resource"""
from http import HTTPStatus

from flask import Blueprint, request

from .utils import get_root_url
from ..db.mock_config_db_client import delete_scheduling_block, \
    get_scheduling_block, get_scheduling_block_ids

BP = Blueprint('scheduling-block', __name__)


@BP.route('/scheduling-block/<block_id>', methods=['GET'])
def get(block_id):
    """Scheduling block detail resource."""
    blocks = get_scheduling_block_ids()
    block = get_scheduling_block(block_id)
    this_index = blocks.index(block_id)
    next_index = this_index + 1 if this_index + 1 < len(blocks) else 0
    prev_index = this_index - 1 if this_index - 1 > 0 else len(blocks) - 1
    response = block
    _url = get_root_url()
    print(_url)
    response['links'] = {
        # 'self': '{}'.format(request.url),
        # 'next': '{}/scheduling-block/{}'.format(_url, blocks[next_index]),
        # 'prev': '{}/scheduling-block/{}'.format(_url, blocks[prev_index]),
        'list': '{}/scheduling-blocks'.format(_url),
        'home': '{}'.format(_url)
    }
    return block


@BP.route('/scheduling-block/<block_id>', methods=['DELETE'])
def delete(block_id):
    """Scheduling block detail resource."""
    try:
        delete_scheduling_block(block_id)
        response = dict(message='Deleted block: _id = {}'.format(block_id))
        response['_links'] = {
            'list': '{}scheduling-blocks'.format(request.url_root)
        }
        return response, HTTPStatus.OK
    except:  # TODO(BM) handle specific exceptions for blocks not existing etc.
        return {'error': 'Unable to delete block.'}, \
            HTTPStatus.BAD_REQUEST

