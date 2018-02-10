# -*- coding: utf-8 -*-
"""SIP Processing Controller Interface (REST)

http://blog.subair.net/make-a-simple-modular-rest-api-using-flask-and-blueprint/
"""
from flask import request
from flask_api import FlaskAPI

from .scheduling_blocks.route import scheduling_blocks_api
from .scheduling_block.route import scheduling_block_api

APP = FlaskAPI(__name__)

APP.register_blueprint(scheduling_blocks_api)
APP.register_blueprint(scheduling_block_api)


@APP.route('/')
def root():
    """."""
    return {"_links": {
        "message": "Welcome to the SIP Processing Controller interface",
        "items": [
            {"href": "{}scheduling-blocks".format(request.url)},
            {"href": "{}processing-blocks".format(request.url)}
        ]
    }}


@APP.route('/processing-blocks', methods=['GET'])
def processing_block_list():
    """Processing blocks list resource."""
    return {}


@APP.route('/processing-block/<block_id>', methods=['GET', 'DELETE'])
def processing_block_detail():
    """Processing blocks detail resource."""
    return {}
