# -*- coding: utf-8 -*-
"""Sub array route"""
import logging
from http import HTTPStatus
import re

from flask import Blueprint, request

from .utils import add_scheduling_block, get_root_url
from ..db.client import ConfigDb

BP = Blueprint('sub-array', __name__)
DB = ConfigDb()
LOG = logging.getLogger('SIP.EC.PCI')


@BP.route('/sub-array/<sub_array_id>', methods=['GET'])
def _get(sub_array_id):
    """Sub array detail resource.

    This method will list scheduling blocks and processing blocks
    in the specified sub-array.
    """
    if not re.match(r'^subarray-0[0-9]|subarray-1[0-5]$', sub_array_id):
        response = dict(error='Invalid sub-array ID specified "{}" does not '
                              'match sub-array ID naming convention '
                              '(ie. subarray-[00-15]).'.
                        format(sub_array_id))
        return response, HTTPStatus.BAD_REQUEST
    if sub_array_id not in DB.get_sub_array_ids():
        response = dict(error='Sub-array "{}" does not currently exist. '
                              'Known sub-arrays = {}'
                        .format(sub_array_id, DB.get_sub_array_ids()))
        return response, HTTPStatus.NOT_FOUND

    block_ids = DB.get_sub_array_sbi_ids(sub_array_id)
    _blocks = [b for b in DB.get_block_details(block_ids)]
    response = dict(scheduling_blocks=[])
    _url = get_root_url()
    for block in _blocks:
        block['links'] = {
            'self': '{}/scheduling-block/{}'.format(_url, block['id'])
        }
        response['scheduling_blocks'].append(block)
    response['links'] = {
        'self': '{}'.format(request.url),
        'list': '{}/sub-arrays'.format(_url),
        'home': '{}'.format(_url),
    }
    return response, HTTPStatus.OK


@BP.route('/sub-array/<sub_array_id>', methods=['POST'])
def _create(sub_array_id):
    """Create / register a Scheduling Block instance with SDP."""
    config = request.data
    config['sub_array_id'] = 'subarray-{:02d}'.format(sub_array_id)
    return add_scheduling_block(config)


@BP.route('/sub-array/<sub_array_id>/scheduling-blocks', methods=['GET'])
def _get_scheduling_blocks(sub_array_id):
    """Return the list of scheduling blocks instances associated with the sub
    array"""
    block_ids = DB.get_sub_array_sbi_ids(sub_array_id)
    return block_ids, HTTPStatus.OK


@BP.route('/sub-array/<sub_array_id>/scheduling-block/<block_id>',
          methods=['GET'])
def _get_scheduling_block(sub_array_id, block_id):
    """Return the list of scheduling blocks instances associated with the sub
    array"""
    block_ids = DB.get_sub_array_sbi_ids(sub_array_id)
    if block_id in block_ids:
        block = DB.get_block_details([block_id]).__next__()
        return block, HTTPStatus.OK

    return dict(error="unknown id"), HTTPStatus.NOT_FOUND
