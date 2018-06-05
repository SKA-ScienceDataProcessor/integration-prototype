# -*- coding: utf-8 -*-
"""Processing Controller API default route."""
import time
from http import HTTPStatus

from flask import Blueprint
from .utils import get_root_url
from ..db.client import ConfigDb


BP = Blueprint('processing_controller_health:', __name__)
DB = ConfigDb()


START_TIME = time.time()


@BP.route('/health')
def api_health():
    """Check the health of this service"""
    response = dict(state='OK', uptime=(time.time() - START_TIME),
                    links=dict(api_root='{}'.format(get_root_url())))
    try:
        DB.get_sub_array_ids()
    except ConnectionError as error:
        response['state'] = 'ERROR'
        response['message'] = str(error)
    return response, HTTPStatus.OK
