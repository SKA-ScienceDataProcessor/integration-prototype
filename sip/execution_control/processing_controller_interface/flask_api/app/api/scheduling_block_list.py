# -*- coding: utf-8 -*-
"""Scheduling Block Instance List API resource."""
from http import HTTPStatus
from random import choice
import logging


from flask import Blueprint, request
from jsonschema import ValidationError

from .utils import get_root_url

from ..db.client import ConfigDbClient


DB = ConfigDbClient()
BP = Blueprint("scheduling-blocks", __name__)
LOG = logging.getLogger('SIP.PCI')


@BP.route('/scheduling-blocks', methods=['GET'])
def get():
    """Return list of Scheduling Blocks Instances known to SDP ."""
    LOG.debug('GET list of SBIs.')
    _url = get_root_url()
    response = dict(scheduling_blocks=[],
                    links=dict(self='{}'.format(request.url),
                               home='{}'.format(_url)))
    blocks = response['scheduling_blocks']
    block_ids = sorted(DB.get_scheduling_block_ids())
    LOG.debug('Current list of SBI IDs: {}'.format(block_ids))
    _blocks = DB.get_block_details(block_ids)
    LOG.debug('Constructing list of processing blocks.')

    for block in _blocks:
        block_id = block['id']
        LOG.debug('Requesting details of block: %s', block_id)
        block['num_processing_blocks'] = 0
        if 'processing_blocks' in block:
            block['num_processing_blocks'] = len(block['processing_blocks'])
        temp = ['OK'] * 10 + ['WAITING'] * 4 + ['FAILED'] * 2
        block['status'] = choice(temp)
        try:
            del block['processing_blocks']
        except KeyError:
            pass
        block['links'] = {
            'detail': '{}/scheduling-block/{}' .format(_url, block_id)
        }
        blocks.append(block)
    return response, HTTPStatus.OK


@BP.route('/scheduling-blocks', methods=['POST'])
def create():
    """Create / register a Scheduling Block instance with SDP."""
    config = request.data
    try:
        DB.set_scheduling_block(config)
    except ValidationError as error:
        error_dict = error.__dict__
        for key in error_dict:
            error_dict[key] = error_dict[key].__str__()
        error_response = dict(message="Failed to add scheduling block",
                              reason="JSON validation error",
                              details=error_dict)
        return error_response, HTTPStatus.BAD_REQUEST

    _url = get_root_url()

    response = config
    response['links'] = {
        'self': '{}/{}'.format(request.base_url,
                                               config['id']),
        'next': 'TODO',
        'previous': 'TODO',
        'list': '{}'.format(request.url),
        'home': '{}'.format(_url)
    }
    return response, HTTPStatus.ACCEPTED


@BP.route('/scheduling-blocks/table')
def get_table():
    """Provides table of scheduling block instance metadata for use with AJAX
    tables"""
    response = dict(blocks=[])
    block_ids = DB.get_scheduling_block_ids()
    for ii, block_id in enumerate(block_ids):
        block = DB.get_block_details(block_id)
        info = [
            ii,
            block['id'],
            block['sub_array_id'],
            len(block['processing_blocks'])
        ]
        response['blocks'].append(info)
    return response, HTTPStatus.OK
