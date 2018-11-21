# -*- coding: utf-8 -*-
"""Processing Controller API default route."""
from http import HTTPStatus

from flask import Blueprint, request

BP = Blueprint('processing_controller:', __name__)


@BP.route('/', methods=['GET'])
def root():
    """Placeholder root url for the PCI.

    Ideally this should never be called!
    """
    response = {
        "links": {
            "message": "Welcome to the SIP Processing Controller Interface",
            "items": [
                {"href": "{}health".format(request.url)},
                {"href": "{}subarrays".format(request.url)},
                {"href": "{}scheduling_blocks".format(request.url)},
                {"href": "{}processing_blocks".format(request.url)}
            ]
        }
    }
    return response, HTTPStatus.OK
