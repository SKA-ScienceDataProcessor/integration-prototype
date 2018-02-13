# -*- coding: utf-8 -*-
"""Scheduling blocks route"""
import os

from flask import Blueprint, request
from flask_api import status
import pymongo
from pymongo import MongoClient, errors
import jsonschema
from jsonschema import validate

# from ..app import DATABASE_URL
# from ..app import CLIENT, BLOCKS
from ..schema.schema import SCHEDULING_BLOCK_SCHEMA

DATABASE_URL = os.getenv('DATABASE_URL', 'mongodb://localhost:27017')
CLIENT = MongoClient(DATABASE_URL,
                     serverSelectionTimeoutMS=500,
                     connectTimeoutMS=500,
                     connect=True)
DB = CLIENT.processing_controller_interface
BLOCKS = DB.scheduling_blocks


scheduling_blocks_api = Blueprint('scheduling_blocks_api', __name__)


@scheduling_blocks_api.route('/scheduling-blocks', methods=['GET', 'POST'])
def scheduling_block_list():
    """Scheduling blocks list resource."""
    try:
        CLIENT.server_info()
    except pymongo.errors.ServerSelectionTimeoutError:
        return {'error': 'Unable to connect to database: {}'.
                format(DATABASE_URL)}, status.HTTP_500_INTERNAL_SERVER_ERROR

    if request.method == 'POST':
        data = request.data
        try:
            validate(data, SCHEDULING_BLOCK_SCHEMA)
        except jsonschema.exceptions.SchemaError as error:
            return {'error': 'Invalid scheduling block Schema: {}'.
                    format(error.message)}, status.HTTP_400_BAD_REQUEST

        block_id = 0
        for block in BLOCKS.find({}):
            block_id = max(block_id, int(block['_id'].lstrip('sb-')))
        data['_id'] = 'sb-%02i' % (block_id + 1)
        BLOCKS.insert_one(data)
        response = data
        response['links'] = {
            'self': '{}scheduling-block/{}'.format(request.url_root,
                                                   data['_id']),
            'list': '{}'.format(request.url)

        }
        return response, status.HTTP_202_ACCEPTED

    # request.method == GET
    response = []
    for block in BLOCKS.find({}):
        block['links'] = {
            'self': '{}scheduling-block/{}'.format(request.url_root,
                                                   block['_id'])
        }
        response.append(block)
    return response, status.HTTP_200_OK
