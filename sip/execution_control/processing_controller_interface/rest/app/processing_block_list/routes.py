# -*- coding: utf-8 -*-
"""Scheduling blocks route"""
from flask import Blueprint, request
from flask_api import status

from ..mock_config_db_client import get_processing_block_ids, \
                                    get_processing_block


API = Blueprint('processing_block_list', __name__)


@API.route('/processing-blocks', methods=['GET'])
def get_processing_block_list():
    """Return the list of Processing Blocks known to SDP."""
    response = []
    block_ids = get_processing_block_ids()
    for block_id in block_ids:
        block = get_processing_block(block_id)
        # block['links'] = {
        #     'self': '{}scheduling-block/{}'.format(request.url_root,
        #                                            block_id)
        # }
        response.append(block)
    return response, status.HTTP_200_OK


