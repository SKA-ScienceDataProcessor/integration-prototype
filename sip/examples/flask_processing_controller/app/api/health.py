# -*- coding: utf-8 -*-
"""Processing Controller API default route."""
import time
from http import HTTPStatus

from flask import Blueprint
from .utils import get_root_url


BP = Blueprint('processing_controller_health', __name__)


START_TIME = time.time()


@BP.route('/health')
def get():
    """Check the health of this service"""
    uptime = time.time() - START_TIME
    response = dict(uptime=f'{uptime:.2f}s',
                    links=dict(root='{}'.format(get_root_url())))

    # TODO(BM) check if we can connect to the config database ...
    # try:
    #     DB.get_sub_array_ids()
    # except ConnectionError as error:
    #     response['state'] = 'ERROR'
    #     response['message'] = str(error)
    return response, HTTPStatus.OK
