# -*- coding: utf-8 -*-
"""Tests of the Docker Stack API.

Run from the dask_ee_interface folder with:

    py.test --pylint --codestyle -s -v --durations=3 \
        --pylint-rcfile=../../../.pylintrc tests

"""
from ..docker_stack import Stack


def test_stack_list():
    """."""
    stack = Stack()
    print('STACK LIST', stack.list())
