# -*- coding: utf-8 -*-
"""Sub array route"""
from flask import Blueprint, request
from flask_api import status

from ..mock_config_db_client import get_sub_array_ids, \
                                    get_sub_array_scheduling_block_ids


API = Blueprint('sub_array_list', __name__)


@API.route('/sub-arrays', methods=['GET'])
def get_sub_array_list():
    """Sub array list resource.

    This method will list all sub-arrays known to SDP.
    """
    sub_array_ids = get_sub_array_ids()
    response = dict(sub_arrays=[])
    for array_id in sub_array_ids:
        array_summary = dict(sub_arrary_id=array_id)
        block_ids = get_sub_array_scheduling_block_ids(array_id)
        array_summary['num_scheduling_blocks'] = len(block_ids)
        array_summary['links'] = {
            'detail': '{}sub-array/{}'.format(request.url_root,
                                              array_id)
        }
        response['sub_arrays'].append(array_summary)
    return response, status.HTTP_200_OK
