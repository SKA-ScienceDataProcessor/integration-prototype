# -*- coding: utf-8 -*-
"""Sub array route"""
from flask import Blueprint, request
from flask_api import status

from .utils import get_root_url
from ..db.mock_config_db_client import get_sub_array_ids, \
    get_sub_array_scheduling_block_ids

BP = Blueprint('sub-array-list', __name__)


@BP.route('/sub-arrays', methods=['GET'])
def get():
    """Sub array list resource.

    This method will list all sub-arrays known to SDP.
    """
    _url = get_root_url()
    sub_array_ids = get_sub_array_ids()
    response = dict(sub_arrays=[])
    for array_id in sub_array_ids:
        array_summary = dict(sub_arrary_id=array_id)
        block_ids = get_sub_array_scheduling_block_ids(array_id)
        array_summary['num_scheduling_blocks'] = len(block_ids)
        array_summary['links'] = {
            'detail': '{}/sub-array/{}'.format(_url, array_id)
        }
        response['sub_arrays'].append(array_summary)
    response['links'] = dict(self=request.url, home=_url)
    return response, status.HTTP_200_OK
