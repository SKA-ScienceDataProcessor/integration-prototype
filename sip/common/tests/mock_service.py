# coding: utf-8
""" Trivial mock service.

Used by the Docker Swarm PaaS unittest.

Contains an RPyC server which is started on a port specified
by the first command line argument.
"""
import platform
import sys
import threading
import time

import rpyc


class MyService(rpyc.Service):
    """ RPyC service interface class.

     This defines the RPyC interface exposed by the mock service.
     """

    def on_connect(self):
        """ Method called when the connection is made.
        """
        pass

    def on_disconnect(self):
        """ Method called when disconnecting.
        """
        pass

    # pylint: disable=no-self-use
    def exposed_hello(self):
        """ Exposed hello method.
        """
        return 'hello from {}'.format(platform.uname()[1])


if __name__ == '__main__':
    from rpyc.utils.server import ThreadedServer
    SERVER = ThreadedServer(MyService, port=int(sys.argv[1]))
    THREAD = threading.Thread(target=SERVER.start)
    THREAD.setDaemon(True)
    THREAD.start()
    while True:
        time.sleep(0.1)
