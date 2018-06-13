# -*- coding: utf-8 -*-
"""."""
import time
from dask.distributed import Client, progress
# This fails as the worker container does not have astropy :-)
# from astropy.cosmology import WMAP9 as cosmo


def set_value(x):
    # return cosmo.H(0).value
    return 2

def square(x):
    time.sleep(10.0)
    return x**2

def neg(x):
    time.sleep(10.0)
    return -x

def main():
    client = Client('localhost:8786')
    print('here A')
    A = client.map(set_value, range(100))
    print('here B')
    B = client.map(square, A)
    print('here C')
    C = client.map(neg, B)
    print('here D')
    total = client.submit(sum, C)
    print('here E')
    print(progress(total))
    print(total.result())

if __name__ == '__main__':
    main()
