# coding=utf-8
"""Tango Master Commands."""
from tango import DeviceProxy
md = DeviceProxy('sip_sdp/elt/master')
print(md.version)
