# coding=utf-8
"""Misc functions for interacting with datetime."""
from datetime import datetime
import sys


def datetime_from_isoformat(value: str):
    """Return a datetime object from an isoformat string.

    Args:
        value (str): Datetime string in isoformat.

    """
    if sys.version_info >= (3, 7):
        return datetime.fromisoformat(value)

    return datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%f')
