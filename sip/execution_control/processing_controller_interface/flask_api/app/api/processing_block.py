# -*- coding: utf-8 -*-
"""Scheduling blocks route"""
from flask import Blueprint, request
from http import HTTPStatus

from .utils import get_root_url
from ..db.mock_config_db_client import get_processing_block, \
                                       delete_processing_block


BP = Blueprint('processing-block', __name__)


@BP.route('/processing-block/<block_id>', methods=['GET'])
def get(block_id):
    """Processing block detail resource."""
    _url = get_root_url()
    try:
        block = get_processing_block(block_id)
        response = block

        response['links'] = {
            'self': '{}'.format(request.url),
            'list': '{}/processing-blocks'.format(_url),
            'home': '{}'.format(_url)
        }
        return block
    except KeyError as error:
        response = dict(message='Unable to GET Processing Block',
                        id='{}'.format(block_id),
                        reason=error.__str__())
        response['links'] = {
            'list': '{}/processing-blocks'.format(_url),
            'home': '{}'.format(_url)
        }
        return response, HTTPStatus.BAD_REQUEST


@BP.route('/processing-block/<block_id>', methods=['DELETE'])
def delete(block_id):
    """Processing block detail resource."""
    try:
        delete_processing_block(block_id)
        response = dict(message='Deleted block',
                        id='{}'.format(block_id))
        response['_links'] = {
            'list': '{}processing-blocks'.format(request.url_root)
        }
        return response, HTTPStatus.OK
    except:  # TODO(BM) handle specific exceptions for blocks not existing etc.
        return (dict(error='Unable to delete block', id='{}'.format(block_id)),
                HTTPStatus.BAD_REQUEST)
