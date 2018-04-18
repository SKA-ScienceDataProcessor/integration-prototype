# -*- coding: utf-8 -*-
"""Test Tango device server"""
import time
import sys

import tango
from tango import DeviceClass
from tango.server import Device, attribute, command, pipe


class Test(Device):
    """Test Tango device class."""

    @attribute
    def time(self):
        return time.time()

    @command(dtype_in=str, dtype_out=str)
    def echo(self, value):
        return value

    @pipe
    def info(self):
        return 'Information', dict(foo=2, bar='hello')


class TestClass(DeviceClass):
    class_property_list = {}
    device_property_list = {}


if __name__ == '__main__':
    util = tango.Util(sys.argv)
    util.add_class(TestClass, Test, 'Test')

    # U = tango.Util.instance()
    # U.server_init()
    Test.run_server()
