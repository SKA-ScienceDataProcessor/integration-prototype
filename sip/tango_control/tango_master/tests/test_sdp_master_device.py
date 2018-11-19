# coding=utf-8
"""Test client commands for the SDP Master device."""
import tango
from _version import __version__


def test_sdp_master():
    master = tango.DeviceProxy('sip_sdp/elt/master')
    # print(master.get_attribute_list())
    assert master.version == __version__
    assert master.state() == tango.DevState.STANDBY
    assert master.current_sdp_state == 'unknown'
    assert master.target_sdp_state == 'unknown'
    print(master.resource_availability)
    print(type(master.resource_availability[0]))
    # assert 'nodes_free' in master.resource_availability
    assert master.health_check >= 0

