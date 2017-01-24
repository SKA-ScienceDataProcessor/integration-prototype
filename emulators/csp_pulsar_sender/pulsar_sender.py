# -*- coding: utf-8 -*-
import json
from ftplib import FTP

"""Module to send pulsar data, FTP client.

The pulsar data is sent using stream mode.
Data is sent as a continuous stream, stream, relieving FTP from
doing any processing

This module makes use of the PrsSender class to send the pulsar data.

"""
__author__ = 'Nijin Thykkathu'


class PrsSender:
    def __init__(self):
        """Creates and initialises the ftp client"""
        self._host = 'localhost'
        self._port = 7878
        self._ftp = FTP()
        self._ftp.connect(self._host, self._port)
        self._ftp.login(user='user', passwd='12345')
        self._ftp.set_pasv(False)

        # Following code sends the command MODE B to the sever
        # Used for testing to see if this initialises block mode
        # self._ftp.sendcmd('MODE B')

    def send(self, config, log, obs_id, beam_id):
        """
        Send the pulsar data to the ftp server

        Args:
            config (dict): Dictionary of settings
            log (logging.Logger): Python logging object
            obs_id: observation id
            beam_id: beam id
        """
        log.info('Starting Pulsar Data Transfer...')
        socket = self._ftp.transfercmd('STOR {0}_{1}'.format(obs_id, beam_id))
        socket.send(json.dumps(config).encode())
        socket.send(bytearray(1000 * 1000))
        config['metadata']['name'] = 'candidate two'
        socket.send(json.dumps(config).encode())
        socket.send(bytearray(1000 * 1000))
        socket.close()
        log.info('Pulsar Data Transfer Completed...')
