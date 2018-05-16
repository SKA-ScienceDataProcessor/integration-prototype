# -*- coding: utf-8 -*-
"""Scheduling blocks route"""
import os

from flask import Blueprint, request
from flask_api import status
import pymongo
from pymongo import MongoClient, errors
import jsonschema
from jsonschema import validate

from ..schema.schema import SCHEDULING_BLOCK_SCHEMA

DATABASE_URL = os.getenv('DATABASE_URL', 'mongodb://localhost:27017')
CLIENT = MongoClient(DATABASE_URL,
                     serverSelectionTimeoutMS=500,
                     connectTimeoutMS=500,
                     connect=True)
DB = CLIENT.processing_controller_interface
BLOCKS = DB.scheduling_blocks


scheduling_block_api = Blueprint('scheduling_block_api', __name__)


@scheduling_block_api.route('/scheduling-block/<block_id>',
                            methods=['GET', 'DELETE'])
def scheduling_block_detail(block_id):
    """Scheduling block detail resource."""
    try:
        CLIENT.server_info()
    except pymongo.errors.ServerSelectionTimeoutError:
        return {'error': 'Unable to connect to database: {}'.
                format(DATABASE_URL)}, status.HTTP_500_INTERNAL_SERVER_ERROR

    if request.method == 'DELETE':
        result = BLOCKS.delete_one({'_id': block_id})
        if result.deleted_count == 1:
            response = dict(message='Deleted block: _id = {}'.format(block_id))
            response['_links'] = {
                'list': '{}scheduling-blocks'.format(request.url_root)
            }
            return response, status.HTTP_200_OK
        return {'error': 'Unable to delete block.'}, \
            status.HTTP_400_BAD_REQUEST

    block = BLOCKS.find_one({'_id': block_id})
    response = block
    response['_links'] = {
        'self': '{}'.format(request.url),
        'list': '{}scheduling-blocks'.format(request.url_root)
    }
    return block
