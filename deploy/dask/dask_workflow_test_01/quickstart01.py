# -*- coding: utf-8 -*-
"""Test Workflow for playing with deployment options."""
from dask.distributed import Client, progress
import time


def set_value(value):
    """."""
    return value


def square(value):
    """Square the specified value."""
    time.sleep(2.0)
    return value**2


def neg(value):
    """Return a negative copy of the value """
    time.sleep(2.0)
    return -value


def main():
    client = Client('localhost:8786')
    A = client.map(set_value, range(100))
    B = client.map(square, A)
    C = client.map(neg, B)
    total = client.submit(sum, C)
    print(progress(total))
    print(total.result())

if __name__ == '__main__':
    main()
