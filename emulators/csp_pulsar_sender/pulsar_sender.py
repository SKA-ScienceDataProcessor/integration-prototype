# -*- coding: utf-8 -*-
import json
from ftplib import FTP

"""Module to send pulsar data, FTP client."""
__author__ = 'Nijin Thykkathu'


class PrsSender:
    def __init__(self):
        # Initialise ftp client
        self._host = 'localhost'
        self._port = 7878
        self._ftp = FTP()
        self._ftp.connect(self._host, self._port)
        self._ftp.login(user='user', passwd='12345')
        self._ftp.set_pasv(False)
        # self._ftp.sendcmd('MODE B')

    def send(self, config, obs_id, beam_id):
        # Two sets of file are send
        socket = self._ftp.transfercmd('STOR {0}_{1}'.format(obs_id, beam_id))
        socket.send(json.dumps(config).encode())
        socket.send(bytearray(1000 * 1000))
        # Changing the name of the metadata - For testing
        config['metadata']['name'] = 'candidate two'
        socket.send(json.dumps(config).encode())
        socket.send(bytearray(1000 * 1000))
        socket.close()
