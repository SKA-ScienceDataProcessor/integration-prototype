# -*- coding: utf-8 -*-
"""Scheduling Block Instance List API resource."""
import logging
from http import HTTPStatus
from random import choice

from flask import Blueprint, request

from .utils import add_scheduling_block, get_root_url
from ..db.client import ConfigDb

DB = ConfigDb()
BP = Blueprint("scheduling-blocks", __name__)
LOG = logging.getLogger('SIP.EC.PCI')


@BP.route('/scheduling-blocks', methods=['GET'])
def get():
    """Return list of Scheduling Blocks Instances known to SDP ."""
    LOG.debug('GET list of SBIs.')

    # Construct response object.
    _url = get_root_url()
    response = dict(scheduling_blocks=[],
                    links=dict(home='{}'.format(_url)))

    # Get ordered list of SBI ID's.
    block_ids = DB.get_sched_block_instance_ids()

    # Loop over SBIs and add summary of each to the list of SBIs in the
    # response.
    for block in DB.get_block_details(block_ids):
        block_id = block['id']
        LOG.debug('Adding SBI %s to list', block_id)
        LOG.debug(block)

        block['num_processing_blocks'] = len(block['processing_block_ids'])

        temp = ['OK'] * 10 + ['WAITING'] * 4 + ['FAILED'] * 2
        block['status'] = choice(temp)
        try:
            del block['processing_block_ids']
        except KeyError:
            pass
        block['links'] = {
            'detail': '{}/scheduling-block/{}' .format(_url, block_id)
        }
        response['scheduling_blocks'].append(block)
    return response, HTTPStatus.OK


@BP.route('/scheduling-blocks', methods=['POST'])
def create():
    """Create / register a Scheduling Block instance with SDP."""
    config = request.data
    return add_scheduling_block(config)


@BP.route('/scheduling-blocks/table')
def get_table():
    """Provides table of scheduling block instance metadata for use with AJAX
    tables"""
    response = dict(blocks=[])
    block_ids = DB.get_sched_block_instance_ids()
    for index, block_id in enumerate(block_ids):
        block = DB.get_block_details([block_id]).__next__()
        info = [
            index,
            block['id'],
            block['sub_array_id'],
            len(block['processing_blocks'])
        ]
        response['blocks'].append(info)
    return response, HTTPStatus.OK
