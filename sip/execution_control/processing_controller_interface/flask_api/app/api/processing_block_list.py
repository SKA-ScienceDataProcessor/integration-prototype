# -*- coding: utf-8 -*-
"""Scheduling blocks route"""
from http import HTTPStatus

from flask import Blueprint, request

from .utils import get_root_url

from ..db.client import ConfigDbClient

BP = Blueprint('processing-blocks', __name__)
DB = ConfigDbClient()


@BP.route('/processing-blocks', methods=['GET'])
def get():
    """Return the list of Processing Blocks known to SDP."""
    _url = get_root_url()
    block_ids = DB.get_processing_block_ids()
    _blocks = [b for b in DB.get_block_details(sorted(block_ids))]
    # FIXME(BM) BUG get_block_details seems not to work for processing blocks
    # as its returning too many!
    assert len(block_ids) == len(_blocks)
    response = dict(num_blocks=len(_blocks), processing_blocks=[])
    for block in _blocks:
        block_id = block['id']
        block['links'] = {
            'detail': ('{}/processing-block/{}'.format(_url, block_id)),
            'scheduling_block': ('{}/scheduling-block/{}'
                                 .format(_url, block_id.split(':')[0]))
        }
        response['processing_blocks'].append(block)
    response['links'] = {
        'self': '{}'.format(request.url),
        'home': '{}'.format(_url)
    }
    return response, HTTPStatus.OK
