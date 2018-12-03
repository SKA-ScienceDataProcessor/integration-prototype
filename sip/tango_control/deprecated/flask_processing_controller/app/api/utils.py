# -*- coding: utf-8 -*-
"""Utility functions used for the Flask Processing Controller Interface"""
from http import HTTPStatus
from functools import wraps

import jsonschema
from flask import request

from config_db.sbi_client import SchedulingBlockDbClient


DB = SchedulingBlockDbClient()


def get_root_url():
    """Return the root URL for this resource."""
    # path = request.path
    # path = path[1:].split('/')
    # path = '/'.join(path[:2])
    # return request.url_root + path
    return request.url_root


def add_scheduling_block(config):
    """Adds a scheduling block to the database, returning a response object"""
    try:
        DB.add_sbi(config)
    except jsonschema.ValidationError as error:
        error_dict = error.__dict__
        for key in error_dict:
            error_dict[key] = error_dict[key].__str__()
        error_response = dict(message="Failed to add scheduling block",
                              reason="JSON validation error",
                              details=error_dict)
        return error_response, HTTPStatus.BAD_REQUEST
    response = dict(config=config,
                    message='Successfully registered scheduling block '
                            'instance with ID: {}'.format(config['id']))
    response['links'] = {
        'self': '{}scheduling-block/{}'.format(request.url_root,
                                               config['id']),
        'list': '{}'.format(request.url),
        'home': '{}'.format(request.url_root)
    }
    return response, HTTPStatus.ACCEPTED


def missing_db_response(func):
    """Decorator to check connection exceptions"""
    @wraps(func)
    def with_exception_handling(*args, **kwargs):
        """Wrapper to check for connection failures"""
        try:
            return func(*args, **kwargs)
        except ConnectionError as error:
            return (dict(error='Unable to connect to Configuration Db.',
                         error_message=str(error),
                         links=dict(root='{}'.format(get_root_url()))),
                    HTTPStatus.NOT_FOUND)
    return with_exception_handling
