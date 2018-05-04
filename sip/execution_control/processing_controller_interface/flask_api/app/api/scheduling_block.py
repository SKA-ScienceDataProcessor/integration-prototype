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
    block = DB.get_block_details([block_id]).__next__()
    response = block
    _url = get_root_url()
    print(_url)
    response['links'] = {
        'list': '{}/scheduling-blocks'.format(_url),
        'home': '{}'.format(_url)
    }
    return block


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

