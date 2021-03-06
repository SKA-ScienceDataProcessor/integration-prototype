# -*- coding: utf-8 -*-
"""SIP Mock Tango Control Processing Controller"""
import logging
from http import HTTPStatus
import os
import sys

from flask import request
from flask_cors import CORS
from flask_api import FlaskAPI

from .api.home import BP as HOME
from .api.health import BP as HEALTH
from .api.subarray_list import BP as SUBARRAY_LIST
# from .api.subarray import BP as SUBARRAY
# from .api.processing_block import BP as PROCESSING_BLOCK
# from .api.processing_block_list import BP as PROCESSING_BLOCK_LIST
# from .api.scheduling_block import BP as SCHEDULING_BLOCK
# from .api.scheduling_block_list import BP as SCHEDULING_BLOCK_LIST


LOG = logging.getLogger('SIP.EC.PCI')
HANDLER = logging.StreamHandler(stream=sys.stdout)
HANDLER.setFormatter(logging.Formatter(
    '%(name)s(%(levelname).6s) %(message)s'))
HANDLER.setLevel(os.getenv('SIP_PCI_LOG_LEVEL', 'WARN'))
LOG.addHandler(HANDLER)
LOG.setLevel(os.getenv('SIP_PCI_LOG_LEVEL', 'WARN'))


APP = FlaskAPI(__name__)
CORS(APP, resources={r"/api/*": {"origins": "*"}})  # needed for the Web GUI?
PREFIX = '/'
APP.register_blueprint(HOME, url_prefix=PREFIX)
APP.register_blueprint(HEALTH, url_prefix=PREFIX)
APP.register_blueprint(SUBARRAY_LIST, url_prefix=PREFIX)
# APP.register_blueprint(SUBARRAY, url_prefix=PREFIX)
# APP.register_blueprint(SCHEDULING_BLOCK_LIST, url_prefix=PREFIX)
# APP.register_blueprint(SCHEDULING_BLOCK, url_prefix=PREFIX)
# APP.register_blueprint(PROCESSING_BLOCK_LIST, url_prefix=PREFIX)
# APP.register_blueprint(PROCESSING_BLOCK, url_prefix=PREFIX)


@APP.route('/')
def home():
    """Temporary helper function to link to the API routes"""
    return dict(links=dict(api='{}{}'.format(request.url, PREFIX[1:]))), \
        HTTPStatus.OK


@APP.route('/<path:path>')
def catch_all(path):
    """Catch all path - return a JSON 404 """
    return (dict(error='Invalid URL: /{}'.format(path),
                 links=dict(root='{}{}'.format(request.url_root, PREFIX[1:]))),
            HTTPStatus.NOT_FOUND)
