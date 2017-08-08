#!/usr/bin/python3


""" Skeleton process to be started by slave

"""
import os
import socket
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__),'..', '..'))

def _sig_handler(signum, frame):
    sys.exit(0)


def run():

    # Read port number
    port = int(sys.argv[1])

    # Bind to socket
    s = socket.socket()
    s.bind(('', port))
    s.listen(1)

    conn, addr = s.accept()
    while(True):
        data = conn.recv(1024)
    conn.close()
    


if __name__ == '__main__':
    run()
