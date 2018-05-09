# -*- coding: utf-8 -*-
"""Processing Controller view default route."""
from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound
from http import HTTPStatus


BP = Blueprint('home', __name__)


@BP.route('/', methods=['GET'])
def get():
    """Processing Controller Interface Home page"""
    try:
        return render_template('home.html')
    except TemplateNotFound:
        abort(HTTPStatus.NOT_FOUND)




