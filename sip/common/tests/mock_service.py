#!/usr/bin/python3

import platform
import rpyc
import sys

class MyService(rpyc.Service):
    def on_connect(self):
        pass

    def on_disconnect(self):
        pass

    def exposed_hello(self):
        return 'hello from {}'.format(platform.uname()[1])

if __name__ == '__main__':
    from rpyc.utils.server import ThreadedServer
    t = ThreadedServer(MyService, port=int(sys.argv[1]))
    t.start()
