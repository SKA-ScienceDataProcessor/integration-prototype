#! /usr/bin/python3
"""Example client for the SDP Master Device."""
import os
import threading
import time
from datetime import datetime

import tango
from tango import DeviceProxy


class HeartBeat:
    """Class for handling heartbeats from the SDP Master."""

    def __init__(self, device_proxy):
        """Create a heartbeat thread."""
        self._device_proxy = device_proxy
        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True
        thread.start()

    def run(self):
        """Run the heartbeat thread."""
        while True:
            heart_beat = self._device_proxy.HeartBeat
            diff = (datetime.utcnow() -
                    datetime.strptime(heart_beat, '%Y-%m-%d %H:%M:%S.%f'))
            seconds = int(diff.total_seconds())
            if seconds > 60:
                print(("WARNING No heartbeat since {} - {} seconds ago -" +
                       " has watchdog died?").format(heart_beat, seconds))
            time.sleep(30)


class CallBack:
    """Class for handling target state change events."""

    def __init__(self, dev_proxy):
        """Create CallBack object for the specified device."""
        self.first_call = True
        period = dev_proxy.get_attribute_poll_period('targetState')
        if period == 0:
            print('Setting polling on attribute "targetState" to 3s')
            dev_proxy.poll_attribute('targetState', 3000)

    def push_event(self, evt):
        """FIXME add docstring."""
        print("In push_event()")
        # pdb.set_trace()
        if self.first_call:
            self.first_call = False
            print('First callback ... not a real change')
            return
        if not evt.err and evt.event == 'change':
            age = int(time.time()) - evt.attr_value.time.tv_sec
            print(evt.attr_value.value, age)


def main():
    """MC client main function."""
    # Connect to the Server
    os.environ['TANGO_HOST'] = 'localhost:20000'
    dev = DeviceProxy('sdp/elt/master')
    _ = HeartBeat(dev)
    callback = CallBack(dev)
    dev.subscribe_event('targetState', tango.EventType.CHANGE_EVENT,
                        callback, [])
    # while True:
    #     time.sleep(10)
    #     print("Still waiting.....")
    state = input('Master Controller state {} Enter target state....'
                  .format(dev.status()))
    print(state)


if __name__ == '__main__':
    main()
