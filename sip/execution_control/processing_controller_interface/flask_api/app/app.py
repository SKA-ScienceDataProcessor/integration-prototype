# -*- coding: utf-8 -*-
"""SIP Processing Controller Interface (REST)"""
from flask_api import FlaskAPI
import logging

from .api.home import BP as HOME
from .api.health import BP as HEALTH
from .api.scheduling_block_list import BP as SCHEDULING_BLOCK_LIST
from .api.scheduling_block import BP as SCHEDULING_BLOCK
from .api.processing_block_list import BP as PROCESSING_BLOCK_LIST
from .api.processing_block import BP as PROCESSING_BLOCK
from .api.sub_array_list import BP as SUB_ARRAY_LIST
from .api.sub_array import BP as SUB_ARRAY


APP = FlaskAPI(__name__)
PREFIX = '/api/v1'
APP.register_blueprint(HOME, url_prefix=PREFIX)
APP.register_blueprint(HEALTH, url_prefix=PREFIX)
APP.register_blueprint(SCHEDULING_BLOCK_LIST, url_prefix=PREFIX)
APP.register_blueprint(SCHEDULING_BLOCK, url_prefix=PREFIX)
APP.register_blueprint(PROCESSING_BLOCK_LIST, url_prefix=PREFIX)
APP.register_blueprint(PROCESSING_BLOCK, url_prefix=PREFIX)
APP.register_blueprint(SUB_ARRAY_LIST, url_prefix=PREFIX)
APP.register_blueprint(SUB_ARRAY, url_prefix=PREFIX)

LOG = logging.getLogger('SIP')
_HANDLER = logging.StreamHandler()
# _HANDLER.setFormatter(logging.Formatter('%(asctime)s.%(msecs)03d - '
#                                         '%(name)s - '
#                                         '%(levelname).1s - '
#                                         '%(message)s',
#                                         '%Y-%m-%d %H:%M:%S'))
_HANDLER.setFormatter(logging.Formatter(
    '%(name)s(%(levelname).6s) %(message)s'))
LOG.addHandler(_HANDLER)
LOG.setLevel(logging.DEBUG)
