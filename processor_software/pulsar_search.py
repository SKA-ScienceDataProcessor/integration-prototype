# -*- coding: utf-8 -*-
"""Module to provide pulsar search receiver function.

This currently consists of the PulsarSearch class which starts
ftp sever and read file using steam protocol and
write to .data and .json file
"""
__author__ = 'Nijin Thykkathu'

import io
import json
import os
import sys

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.filesystems import AbstractedFS
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer


class PrsReceiver(io.BytesIO):
    def __init__(self):
        self.name = 'pulsar timing buffer'

    def close(self):

        # Seek to the start of the buffer
        self.seek(0)
        while True:

            # Copy bytes from the buffer until we reach the end of the JSON
            brace_count = 0
            quoted = False
            json_string = ''
            while True:

                # Read a character
                b = self.read(1)
                if b == b'':
                    return
                c = b.decode()

                # If it is a \ then copy the next character
                if c == '\\':
                    json_string += c
                    json_string += self.read(1).decode()
                    continue

                # If we are inside quotes we just need to detect a closing quote
                if c == '"':
                    if quoted:
                        quoted == False
                    else:
                        quoted == True

                # Otherwise we count the braces
                if c == '{':
                    brace_count += 1
                elif c == '}':
                    brace_count -= 1

                # Copy the character into the JSON string
                json_string += c

                # If the brace count is zero we are done
                if brace_count == 0:
                    break

            # Parse the JSON so that we can get the size of the data array
            meta = json.loads(json_string)
            n_channels = meta['data']['n_channels']
            n_sub_integrations = meta['data']['n_sub_integrations']

            # Save the JSON to a file
            f = open('{0}_{1}_{2}.json'.format( \
                meta['metadata']['observation_id'],
                meta['metadata']['beam_id'],
                meta['metadata']['name']), 'w')
            f.write(json.dumps(meta))
            f.close()

            # Read the data
            data = self.read(n_channels * n_sub_integrations)

            # Write it to a file
            f = open('{0}_{1}_{2}.data'.format( \
                meta['metadata']['observation_id'],
                meta['metadata']['beam_id'],
                meta['metadata']['name']), 'wb')
            f.write(data)
            f.close()


class PrsFileSystem(AbstractedFS):
    def __init__(self, root, cmd_channel):
        super(PrsFileSystem, self).__init__(root, cmd_channel)

    def open(self, filename, mode):
        self._buffer = PrsReceiver()
        return self._buffer


class PrsRun:
    def run(self):
        print("Starting FTP Server")
        sys.stdout.flush()
        # Instantiate a dummy authorizer for managing 'virtual' users
        authorizer = DummyAuthorizer()

        # Define a new user having full r/w permissions and a read-only
        # anonymous user
        authorizer.add_user('user', '12345', '.', perm='elradfmwM')
        authorizer.add_anonymous(os.getcwd())

        # Instantiate FTP handler class
        handler = FTPHandler
        handler.authorizer = authorizer
        handler.abstracted_fs = PrsFileSystem

        # Define a customized banner (string returned when client connects)
        handler.banner = "SKA SDP pulsar search interface."

        # Instantiate FTP server class and listen on 0.0.0.0:7878
        address = ('', 7878)
        server = FTPServer(address, handler)
        print("FTP Server Started")
        sys.stdout.flush()

        # set a limit for connections
        server.max_cons = 256
        server.max_cons_per_ip = 5

        # start ftp server
        server.serve_forever()
