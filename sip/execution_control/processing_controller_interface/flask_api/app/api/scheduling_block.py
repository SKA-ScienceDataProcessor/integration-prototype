# -*- coding: utf-8 -*-
"""Scheduling block details resource"""
from http import HTTPStatus

from flask import Blueprint, request

from .utils import get_root_url

from ..db.client import ConfigDbClient

BP = Blueprint('scheduling-block', __name__)
DB = ConfigDbClient()


@BP.route('/scheduling-block/<block_id>', methods=['GET'])
def get(block_id):
    """Scheduling block detail resource."""
    try:
        block = DB.get_block_details([block_id]).__next__()
    except KeyError:
        return {'error': 'specified block id not found {}'.format(block_id)}, \
               HTTPStatus.NOT_FOUND
    response = block
    _url = get_root_url()
    print(_url)
    response['links'] = {
        'scheduling-blocks': '{}/scheduling-blocks'.format(_url),
        'sub-array': '{}/sub-array/{}'.format(_url, block['sub_array_id']),
        'home': '{}'.format(_url)
    }
    return block, HTTPStatus.OK


@BP.route('/scheduling-block/<block_id>', methods=['DELETE'])
def delete(block_id):
    """Scheduling block detail resource."""
    try:
        DB.delete_scheduling_block(block_id)
        response = dict(message='Deleted block: _id = {}'.format(block_id))
        response['_links'] = {
            'list': '{}scheduling-blocks'.format(request.url_root)
        }
        return response, HTTPStatus.OK
    except:  # TODO(BM) handle specific exceptions for blocks not existing etc.
        return {'error': 'Unable to delete block.'}, \
            HTTPStatus.BAD_REQUEST

