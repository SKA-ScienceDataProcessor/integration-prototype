# -*- coding: utf-8 -*-
"""SIP Processing Controller Interface (REST)."""
import os

from flask import request
from flask_api import FlaskAPI, status
from pymongo import MongoClient


APP = FlaskAPI(__name__)
DB = MongoClient(os.getenv('DATABASE_URL')).master_controller
BLOCKS = DB.scheduling_blocks


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


@APP.route('/scheduling-blocks', methods=['GET', 'POST'])
def scheduling_block_list():
    """Scheduling blocks list resource."""
    if request.method == 'POST':
        data = request.data
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

    response = []
    for block in BLOCKS.find({}):
        block['links'] = {
            'self': '{}scheduling-block/{}'.format(request.url_root,
                                                   block['_id'])
        }
        response.append(block)
    return response, status.HTTP_200_OK


@APP.route('/scheduling-block/<block_id>', methods=['GET', 'DELETE'])
def scheduling_block_detail(block_id):
    """Scheduling block detail resource."""
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


@APP.route('/processing-blocks', methods=['GET'])
def processing_block_list():
    """Processing blocks list resource."""
    return {}


@APP.route('/processing-block/<block_id>', methods=['GET', 'DELETE'])
def processing_block_detail():
    """Processing blocks detail resource."""
    return {}

