# -*- coding: utf-8 -*-
"""SIP Processing Controller Interface (REST)

http://blog.subair.net/make-a-simple-modular-rest-api-using-flask-and-blueprint/
"""
from flask import Flask

from .views.home import BP as HOME
from .views.scheduling_block_list import BP as SCHEDULING_BLOCK_LIST


APP = Flask(__name__)
APP.register_blueprint(HOME)
APP.register_blueprint(SCHEDULING_BLOCK_LIST)



