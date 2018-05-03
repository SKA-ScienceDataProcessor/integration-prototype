# -*- coding: utf-8 -*-
"""Utility functions used for the Flask Processing Controller Interface"""
from flask import request


def get_root_url():
    """Return the root URL for this resource."""
    path = request.path
    path = path[1:].split('/')
    path = '/'.join(path[:2])
    return request.url_root + path
