# -*- coding: utf-8 -*-
"""Sub array route"""
from flask import Blueprint, request
from flask_api import status

from ..mock_config_db_client import get_sub_array_scheduling_block_ids, \
                                    get_scheduling_block


API = Blueprint('sub_array_api', __name__)


@API.route('/sub-array/<sub_array_id>', methods=['GET'])
def get_sub_array_detail(sub_array_id):
    """Sub array detail resource.

    This method will list scheduling blocks and processing blocks
    in the specified sub-array.
    """
    block_ids = get_sub_array_scheduling_block_ids(sub_array_id)
    response = dict(scheduling_blocks=[])
    for block_id in block_ids:
        block = get_scheduling_block(block_id)
        block['links'] = {
            'self': '{}scheduling-block/{}'.format(request.url_root, block_id)
        }
        response['scheduling_blocks'].append(block)
    response['links'] = {
        'home': '{}'.format(request.url_root),
        'self': '{}'.format(request.url)
    }
    return response, status.HTTP_200_OK

