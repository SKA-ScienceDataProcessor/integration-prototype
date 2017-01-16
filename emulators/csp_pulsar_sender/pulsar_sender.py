import json
from ftplib import FTP

class prs_sender:

    def __init__(self):
        self._host = 'localhost'
        self._port = 7878
        self._ftp = FTP()
        self._ftp.connect(self._host, self._port)
        self._ftp.login(user='user', passwd='12345')
        self._ftp.set_pasv(False)
        #self._ftp.sendcmd('MODE B')

    def send(self, obs_id, beam_id):
        meta = {'metadata': { 'name': 'candidate one',
            'observation_id': 1,
            'beam_id': 1 },
            'data': { 'n_channels': 1000,
            'n_sub_integrations': 1000}}

        socket = self._ftp.transfercmd('STOR {0}_{1}'.format(obs_id, beam_id))
        socket.send(json.dumps(meta).encode())
        socket.send(bytearray(1000 * 1000))
        meta['metadata']['name'] = 'candidate two'
        socket.send(json.dumps(meta).encode())
        socket.send(bytearray(1000 * 1000))
        socket.close()

if __name__ == '__main__':
    prs_sender().send(1, 1)
