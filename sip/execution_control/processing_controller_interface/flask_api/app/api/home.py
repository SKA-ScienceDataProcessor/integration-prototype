# -*- coding: utf-8 -*-
"""Processing Controller API default route."""
from http import HTTPStatus

from flask import Blueprint, request

BP = Blueprint('Processing Controller:', __name__)


@BP.route('/', methods=['GET'])
def root():
    """."""
    response = {
        "links": {
            "message": "Welcome to the SIP Processing Controller interface",
            "items": [
                {"href": "{}scheduling-blocks".format(request.url)},
                {"href": "{}processing-blocks".format(request.url)},
                {"href": "{}sub-arrays".format(request.url)}
            ]
        }
    }
    return response, HTTPStatus.OK
