# -*- coding: utf-8 -*-
"""Scheduling blocks route"""
from flask import Blueprint, request
from flask_api import status

from ..mock_config_db_client import get_processing_block, \
                                    delete_processing_block


PROCESSING_BLOCK_API = Blueprint('processing_block_api', __name__)


@PROCESSING_BLOCK_API.route('/processing-block/<block_id>', methods=['GET'])
def get_processing_block_detail(block_id):
    """Processing block detail resource."""
    block = get_processing_block(block_id)
    response = block
    response['_links'] = {
        'self': '{}'.format(request.url),
        'list': '{}processing-blocks'.format(request.url_root)
    }
    return block


@PROCESSING_BLOCK_API.route('/processing-block/<block_id>', methods=['DELETE'])
def delete_processing_block_request(block_id):
    """Processing block detail resource."""
    try:
        delete_processing_block(block_id)
        response = dict(message='Deleted block: _id = {}'.format(block_id))
        response['_links'] = {
            'list': '{}processing-blocks'.format(request.url_root)
        }
        return response, status.HTTP_200_OK
    except:  # TODO(BM) handle specific exceptions for blocks not existing etc.
        return {'error': 'Unable to delete block.'}, \
            status.HTTP_400_BAD_REQUEST
