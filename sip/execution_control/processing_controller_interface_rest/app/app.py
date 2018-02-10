# -*- coding: utf-8 -*-
"""SIP Processing Controller Interface (REST)."""
import os

import redis
from flask import request
from flask_api import FlaskAPI, status


APP = FlaskAPI(__name__)
DB = redis.Redis(host=os.getenv('DATABASE_HOST'))


@APP.route('/')
def root():
    """."""
    return {"_links": {
        "message": "Welcome to the SIP Processing Controller",
        "items": [
            {"href": "{}scheduling-blocks".format(request.url)},
            {"href": "{}processing-blocks".format(request.url)}
        ]
    }}


@APP.route('/scheduling-blocks', methods=['GET', 'POST'])
def scheduling_block_list():
    """Scheduling blocks list resource."""


@APP.route('/scheduling-block/<block_id>', methods=['GET', 'DELETE'])
def scheduling_block_detail():
    """Scheduling block detail resource."""


@APP.route('/processing-blocks', methods=['GET'])
def processing_block_list():
    """Processing blocks list resource."""


@APP.route('/processing-block/<block_id>', methods=['GET', 'DELETE'])
def processing_block_detail():
    """Processing blocks detail resource."""

