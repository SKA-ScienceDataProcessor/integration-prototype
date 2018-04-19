# -*- coding: utf-8 -*-
"""Sub array route"""
from flask import Blueprint, request
from flask_api import status

# from ..mock_config_db_client import get_processing_block, \
#                                     delete_processing_block


API = Blueprint('sub_array_api', __name__)


@API.route('/sub-array/<sub_array_id>', methods=['GET'])
def get_sub_array_detail(sub_array_id):
    """Sub array detail resource.

    This method will list scheduling blocks and processing blocks
    in the specified sub-array.
    """
    # try:
    #     block = get_processing_block(block_id)
    #     response = block
    #     response['links'] = {
    #         'self': '{}'.format(request.url),
    #         'list': '{}processing-blocks'.format(request.url_root),
    #         'home': '{}'.format(request.url_root)
    #     }
    #     return block
    # except KeyError as error:
    #     response = dict(message='Unable to GET Processing Block',
    #                     id='{}'.format(block_id),
    #                     reason=error.__str__())
    #     response['links'] = {
    #         'list': '{}processing-blocks'.format(request.url_root),
    #         'home': '{}'.format(request.url_root)
    #     }
    #     return response, status.HTTP_400_BAD_REQUEST

