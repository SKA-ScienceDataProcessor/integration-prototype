# -*- coding: utf-8 -*-
"""Utility functions used for the Flask Processing Controller Interface"""
from http import HTTPStatus

import jsonschema
from flask import request

from ..db.client import ConfigDb

DB = ConfigDb()


def get_root_url():
    """Return the root URL for this resource."""
    path = request.path
    path = path[1:].split('/')
    path = '/'.join(path[:2])
    return request.url_root + path


def add_scheduling_block(config):
    """Adds a scheduling block to the database, returning a response object"""
    try:
        DB.add_sched_block_instance(config)
    except jsonschema.ValidationError as error:
        error_dict = error.__dict__
        for key in error_dict:
            error_dict[key] = error_dict[key].__str__()
        error_response = dict(message="Failed to add scheduling block",
                              reason="JSON validation error",
                              details=error_dict)
        return error_response, HTTPStatus.BAD_REQUEST
    response = config
    response['links'] = {
        'self': '{}scheduling-block/{}'.format(request.url_root,
                                               config['id']),
        'next': 'TODO',
        'previous': 'TODO',
        'list': '{}'.format(request.url),
        'home': '{}'.format(request.url_root)
    }
    response = []
    return response, HTTPStatus.ACCEPTED
