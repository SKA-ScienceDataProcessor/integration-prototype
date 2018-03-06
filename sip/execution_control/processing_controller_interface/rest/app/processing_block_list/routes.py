# -*- coding: utf-8 -*-
"""Scheduling blocks route"""
from flask import Blueprint, request
from flask_api import status

from ..mock_config_db_client import get_processing_block_ids, \
                                    get_processing_block


API = Blueprint('processing_block_list', __name__)


@API.route('/processing-blocks', methods=['GET'])
def get_processing_block_list():
    """Return the list of Processing Blocks known to SDP."""
    block_ids = get_processing_block_ids()
    response = dict(processing_blocks=[])
    for block_id in block_ids:
        block = get_processing_block(block_id)
        block['links'] = {
            'self': ('{}processing-block/{}'
                     .format(request.url_root,
                             block_id)),
            'scheduling_block': ('{}scheduling-block/{}'
                                 .format(request.url_root,
                                         block_id.split(':')[0]))
        }
        response['processing_blocks'].append(block)
    response['links'] = {
        'home': '{}'.format(request.url_root)
    }
    return response, status.HTTP_200_OK


