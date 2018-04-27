# -*- coding: utf-8 -*-
"""SIP Processing Controller Interface (REST)

http://blog.subair.net/make-a-simple-modular-rest-api-using-flask-and-blueprint/
"""
from flask import request
from flask_api import FlaskAPI, status
import time

from .scheduling_block_list.routes import API as SCHEDULING_BLOCK_LIST
from .scheduling_block.routes import API as SCHEDULING_BLOCK
from .processing_block_list.routes import API as PROCESSING_BLOCK_LIST
from .processing_block.routes import API as PROCESSING_BLOCK
from .sub_array_list.routes import API as SUB_ARRAY_LIST
from .sub_array.routes import API as SUB_ARRAY

APP = FlaskAPI(__name__)

APP.register_blueprint(SCHEDULING_BLOCK_LIST)
APP.register_blueprint(SCHEDULING_BLOCK)
APP.register_blueprint(PROCESSING_BLOCK_LIST)
APP.register_blueprint(PROCESSING_BLOCK)
APP.register_blueprint(SUB_ARRAY_LIST)
APP.register_blueprint(SUB_ARRAY)


START_TIME = time.time()


@APP.route('/')
def root():
    """."""
    return {"links": {
        "message": "Welcome to the SIP Processing Controller interface",
        "items": [
            {"href": "{}scheduling-blocks".format(request.url)},
            {"href": "{}processing-blocks".format(request.url)},
            {"href": "{}sub-arrays".format(request.url)}
        ]
    }}, status.HTTP_200_OK


@APP.route('/health')
def health():
    """."""
    return {
        "state": "ON",
        "uptime": time.time() - START_TIME
    }, status.HTTP_200_OK

