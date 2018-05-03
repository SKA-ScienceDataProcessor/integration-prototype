# -*- coding: utf-8 -*-
"""Processing Controller API default route."""
import time
from http import HTTPStatus

from flask import Blueprint

BP = Blueprint('processing_controller_health:', __name__)


START_TIME = time.time()


@BP.route('/health')
def api_health():
    """."""
    response = {
        "state": "OK",
        "uptime": time.time() - START_TIME
    }
    return response, HTTPStatus.OK



