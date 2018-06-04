# -*- coding: utf-8 -*-
"""Scheduling block details resource"""
import logging
from http import HTTPStatus

from flask import Blueprint

from .utils import get_root_url
from ..db.client import ConfigDb

BP = Blueprint('scheduling-block', __name__)
DB = ConfigDb()
LOG = logging.getLogger('SIP.EC.PCI')


@BP.route('/scheduling-block/<block_id>', methods=['GET'])
def get(block_id):
    """Scheduling block detail resource."""
    try:
        sbi_details = DB.get_block_details([block_id]).__next__()
        sbi_details['processing_blocks'] = []
        pb_ids = sbi_details['processing_block_ids']
        for pb_details in DB.get_block_details(pb_ids):
            sbi_details['processing_blocks'].append(pb_details)
        del sbi_details['processing_block_ids']
        response = sbi_details
        _url = get_root_url()
        response['links'] = {
            'scheduling-blocks': '{}/scheduling-blocks'.format(_url),
            'home': '{}'.format(_url)
        }
        return sbi_details, HTTPStatus.OK

    except IndexError:
        return {'error': 'specified block id not found {}'.format(block_id)}, \
               HTTPStatus.NOT_FOUND


@BP.route('/scheduling-block/<block_id>', methods=['DELETE'])
def delete(block_id):
    """Scheduling block detail resource."""
    _url = get_root_url()
    LOG.debug('Requested delete of SBI %s', block_id)
    try:
        DB.delete_sched_block_instance(block_id)
        response = dict(message='Deleted block: _id = {}'.format(block_id))
        response['_links'] = {
            'list': '{}/scheduling-blocks'.format(_url)
        }
        return response, HTTPStatus.OK
    except RuntimeError as error:
        return dict(error=str(error)), HTTPStatus.BAD_REQUEST

