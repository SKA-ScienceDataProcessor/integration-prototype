# pylint: disable=unused-import
# coding=utf-8
"""Pytest configuration"""
import pytest
from .rest_api_fixtures import (get_test_app, get_db_client, init_db,
                                set_root_url)
