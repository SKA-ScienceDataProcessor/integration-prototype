# -*- coding: utf-8 -*-
"""Scheduling blocks route"""
import logging
from http import HTTPStatus

from flask import Blueprint, request

from .utils import get_root_url, missing_db_response
from ..db.client import ConfigDb


BP = Blueprint('processing-block', __name__)
DB = ConfigDb()
LOG = logging.getLogger('SIP.EC.PCI')


@BP.route('/processing-block/<block_id>', methods=['GET'])
@missing_db_response
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
        return response, HTTPStatus.NOT_FOUND


@BP.route('/processing-block/<block_id>', methods=['DELETE'])
@missing_db_response
def delete(block_id):
    """Processing block detail resource."""
    _url = get_root_url()
    try:
        DB.delete_processing_block(block_id)
        response = dict(message='Deleted block',
                        id='{}'.format(block_id),
                        links=dict(list='{}/processing-blocks'.format(_url),
                                   home='{}'.format(_url)))
        return response, HTTPStatus.OK
    except RuntimeError as error:
        response = dict(error='Failed to delete Processing Block: {}'.
                        format(block_id),
                        reason=str(error),
                        links=dict(list='{}/processing-blocks'.format(_url),
                                   home='{}'.format(_url)))
        return response, HTTPStatus.OK
