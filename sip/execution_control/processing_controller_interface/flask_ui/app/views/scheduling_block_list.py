# -*- coding: utf-8 -*-
"""Scheduling Block Instance List Web UI."""
from flask import Blueprint, abort, render_template, request
from http import HTTPStatus
from jinja2 import TemplateNotFound
import requests


BP = Blueprint('scheduling-blocks', __name__)


def _get_scheduling_block_instance_list():
    """Return list of scheduling block instances"""
    # TODO make call to rest api
    r = requests.get('http://localhost:5000/api/v1/scheduling-blocks')
    return r.json()['scheduling_blocks']


@BP.route('/scheduling-blocks', methods=['GET'])
def _get():
    """View list of Scheduling Block Instances."""
    blocks = _get_scheduling_block_instance_list()
    try:
        return render_template('scheduling_blocks.html', blocks=blocks)
    except TemplateNotFound:
        abort(HTTPStatus.NOT_FOUND)


@BP.route('/scheduling-blocks', methods=['POST'])
def _post():
    # print('-------')
    # print('REQUEST=')
    # print('args:', request.args)
    # print('form:', request.form)
    # print('data:', request.data)
    # print('vals:', request.values)
    # print('files:', request.files)
    # print('-------')
    print(request.form)
    return 'hello', HTTPStatus.OK
    # text = ''
    # blocks = _get_scheduling_block_instance_list()
    # try:
    #     return render_template('scheduling_block_accepted.html',
    #                            blocks=blocks, text=text, form_data=request.form)
    # except TemplateNotFound:
    #     abort(HTTPStatus.NOT_FOUND)
