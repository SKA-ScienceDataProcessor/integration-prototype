# -*- coding: utf-8 -*-
"""Scheduling blocks route"""
import logging
from http import HTTPStatus

from flask import Blueprint, request

from .utils import get_root_url
from ..db.client import ConfigDbClient

BP = Blueprint('processing-blocks', __name__)
DB = ConfigDbClient()
LOG = logging.getLogger('SIP.PCI')


@BP.route('/processing-blocks', methods=['GET'])
def get():
    """Return the list of Processing Blocks known to SDP."""

    # Get list of Processing block Ids
    block_ids = sorted(DB.get_processing_block_ids())
    LOG.debug('GET Processing Block list')
    LOG.debug('Processing Block IDs: %s', block_ids)

    # Construct response object
    _url = get_root_url()
    response = dict(num_processing_blocks=len(block_ids),
                    processing_blocks=list())

    # Loop over blocks and add block summary to response.
    for block in DB.get_block_details(block_ids):
        block_id = block['id']
        LOG.debug('Creating PB summary for %s', block_id)
        block['links'] = dict(
            detail='{}/processing-block/{}'.format(_url, block_id),
            scheduling_block='{}/scheduling-block/{}'
            .format(_url, block_id.split(':')[0])
        )
        response['processing_blocks'].append(block)
    response['links'] = {
        'self': '{}'.format(request.url),
        'home': '{}'.format(_url)
    }
    return response, HTTPStatus.OK
