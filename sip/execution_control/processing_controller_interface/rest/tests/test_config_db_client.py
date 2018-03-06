# -*- coding: utf-8 -*-
"""Test config db client functions used by the Processing Controller Interface

Run with:
    pytest -m tests/test_config_db_client.py
"""
import pytest
import jsonschema
from app.mock_config_db_client import add_scheduling_block


def test_missing_db():
    """Test missing or broken DB connection"""
    # TODO(BM)


def test_add_scheduling_block():
    """Test adding a scheduling block to the DB"""

    # Empty configuration is invalid and will raise an error
    config = {}
    with pytest.raises(jsonschema.ValidationError,
                       message="Expecting Validation Error"):
        add_scheduling_block(config)

    # Minimal required configuration will not raise an error
    config = {
        "id": "sbi-01",
        "sub_array_id": "01",
        "processing_blocks": []
    }
    add_scheduling_block(config)
