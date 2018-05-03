# -*- coding: utf-8 -*-
"""Scheduling blocks route"""
from http import HTTPStatus

from flask import Blueprint, request

from .utils import get_root_url
from ..db.mock.client import get_processing_block, \
    get_processing_block_ids

BP = Blueprint('processing-blocks', __name__)


@BP.route('/processing-blocks', methods=['GET'])
def get():
    """Return the list of Processing Blocks known to SDP."""
    block_ids = get_processing_block_ids()
    response = dict(processing_blocks=[])
    _url = get_root_url()
    for block_id in block_ids:
        block = get_processing_block(block_id)
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
