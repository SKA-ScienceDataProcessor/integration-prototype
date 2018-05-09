# -*- coding: utf-8 -*-
"""Sub array route"""
from flask import Blueprint, request
from flask_api import status

from .utils import get_root_url
from ..db.client import ConfigDbClient

BP = Blueprint('sub-array-list', __name__)
DB = ConfigDbClient()


@BP.route('/sub-arrays', methods=['GET'])
def get():
    """Sub array list resource.

    This method will list all sub-arrays known to SDP.
    """
    _url = get_root_url()
    sub_array_ids = sorted(DB.get_sub_array_ids())
    response = dict(sub_arrays=[])
    for array_id in sub_array_ids:
        array_summary = dict(sub_arrary_id=array_id)
        # FIXME(BM) this seems to be broken / missing
        # block_ids = get_sub_array_scheduling_block_ids(array_id)
        # block_ids = DB.get_scheduling_block_id_using_sub_array_id(array_id)
        block_ids = DB.get_sub_array_scheduling_block_ids(array_id)
        print('block_ids', block_ids)
        array_summary['num_scheduling_blocks'] = len(block_ids)
        array_summary['links'] = {
            'detail': '{}/sub-array/{}'.format(_url, array_id)
        }
        response['sub_arrays'].append(array_summary)
    response['links'] = dict(self=request.url, home=_url)
    return response, status.HTTP_200_OK
