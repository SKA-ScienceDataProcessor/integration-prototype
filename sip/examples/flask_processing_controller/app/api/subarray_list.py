# -*- coding: utf-8 -*-
"""Sub array route"""
import logging

from flask import Blueprint, request
from flask_api import status

from .utils import get_root_url, missing_db_response
from config_db import SchedulingBlockDbClient

BP = Blueprint('subarray_list:', __name__)
DB = SchedulingBlockDbClient()
LOG = logging.getLogger('SIP.EC.PCI')


@BP.route('/subarrays', methods=['GET'])
@missing_db_response
def get():
    """Subarray list.

    This method will list all sub-arrays known to SDP.
    """
    _url = get_root_url()
    LOG.debug('GET Sub array list')

    sub_array_ids = sorted(DB.get_sub_array_ids())

    response = dict(sub_arrays=[])
    for array_id in sub_array_ids:
        array_summary = dict(sub_arrary_id=array_id)
        block_ids = DB.get_sub_array_sbi_ids(array_id)
        LOG.debug('Subarray IDs: %s', array_id)
        LOG.debug('SBI IDs: %s', block_ids)
        array_summary['num_scheduling_blocks'] = len(block_ids)
        array_summary['links'] = {
            'detail': '{}/sub-array/{}'.format(_url, array_id)
        }
        response['sub_arrays'].append(array_summary)
    response['links'] = dict(self=request.url, home=_url)
    return response, status.HTTP_200_OK


@BP.route('/subarrays/schedule', methods=['POST'])
@missing_db_response
def post():
    """Generate a SBI."""
    _url = get_root_url()
    LOG.debug("POST subarray SBI.")

    # TODO(BM) generate sbi_config .. see report ...
    # ... will need to add this as a util function on the db...
    sbi_config = {}

    DB.add_sbi(sbi_config)

    response = dict()
    return response, status.HTTP_200_OK
