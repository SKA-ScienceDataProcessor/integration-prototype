# -*- coding: utf-8 -*-
"""Unit tests of the root / common resource(s) provided by the PCI"""
import json
from http import HTTPStatus
import pytest


@pytest.mark.usefixtures("app")
def test_invalid_url(app):
    """Test requesting an invalid URL"""
    response = app.get('/foo')
    assert response.mimetype == 'application/json'
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert 'error' in json.loads(response.get_data())


@pytest.mark.usefixtures("app")
def test_get_root(app):
    """Test GET of the root URL."""
    response = app.get('/')
    assert response.mimetype == 'application/json'
    assert response.status_code == HTTPStatus.OK
    data = json.loads(response.get_data())
    assert 'links' in data


@pytest.mark.usefixtures("app", "root_url")
def test_health(app, root_url):
    """Test the health URL"""
    response = app.get(root_url + 'health')
    assert response.mimetype == 'application/json'
    assert response.status_code == HTTPStatus.OK
    data = json.loads(response.get_data())
    assert 'state' in data
    assert 'uptime' in data
