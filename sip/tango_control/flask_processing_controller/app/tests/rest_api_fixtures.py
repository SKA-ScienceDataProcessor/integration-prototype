# -*- coding: utf-8 -*-
"""Test fixtures for testing the Flask Rest API"""
import pytest

from ..app import APP
from ..db.client import ConfigDb
from ..db.init import add_scheduling_blocks


@pytest.fixture(name='db_client', scope='session')
def get_db_client():
    """Fixture: Create config db client"""
    return ConfigDb()


@pytest.fixture(name='app', scope='session')
def get_test_app():
    """Fixture: Create test Flask APP"""
    APP.config['TESTING'] = True
    APP.config['DEBUG'] = False
    APP.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
    app = APP.test_client()
    return app


@pytest.fixture(name='root_url', scope='session')
def set_root_url():
    """Fixture: API root url"""
    return "/api/v1/"


@pytest.fixture(name='init_db', scope='module')
def init_db():
    """Test fixture: initialise the database with 10 SBIs"""
    add_scheduling_blocks(10, clear=True)
