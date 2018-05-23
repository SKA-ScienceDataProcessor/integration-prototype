# -*- coding: utf-8 -*-
"""Scheduling blocks route"""
from http import HTTPStatus

from flask import Blueprint, request

from .utils import get_root_url

from ..db.client import ConfigDbClient


BP = Blueprint('processing-block', __name__)
DB = ConfigDbClient()


@BP.route('/processing-block/<block_id>', methods=['GET'])
def get(block_id):
    """Processing block detail resource."""
    _url = get_root_url()
    try:
        block = DB.get_block_details([block_id]).__next__()
        response = block

        response['links'] = {
            'self': '{}'.format(request.url),
            'list': '{}/processing-blocks'.format(_url),
            'home': '{}'.format(_url)
        }
        return block
    except IndexError as error:
        response = dict(message='Unable to GET Processing Block',
                        id='{}'.format(block_id),
                        error=error.__str__())
        response['links'] = {
            'list': '{}/processing-blocks'.format(_url),
            'home': '{}'.format(_url)
        }
        return response, HTTPStatus.BAD_REQUEST


@BP.route('/processing-block/<block_id>', methods=['DELETE'])
def delete(block_id):
    """Processing block detail resource."""
    _url = get_root_url()
    DB.delete_processing_blocks([block_id])
    # Construct response object
    response = dict(message='Deleted block',
                    id='{}'.format(block_id),
                    links=dict(list='{}/processing-blocks'.format(_url),
                               home='{}'.format(_url)))
    return response, HTTPStatus.OK
