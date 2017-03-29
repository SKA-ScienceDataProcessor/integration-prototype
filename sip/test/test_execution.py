# -*- coding: utf-8 -*-
"""Script to that can be used to run SIP modules.

Current modules:
- Master Controller RPC interface.
- CSP visibility emulator
"""
import subprocess
import rpyc
import time
import select

DEBUG = False


class TestSipRunner():
    """Class to run SIP modules.

    Modules are registered into this class by defining a 'run_{module}' method.
    """

    def __init__(self):
        """Sets up a command line parser, initialises logging and runs the
        specified module.
        """

        # Start master controller
        self._init_master()

    def test_master_rpc(self):
        """Method to talk to the RPC interface to the master controller."""
        print('Starting full execution test.')

        # Connect to the Master Controllers RPC interface.
        try:
            conn = rpyc.connect(host='localhost', port=12345)
        except ConnectionRefusedError:
            self._log.error('Unable to connect to Master Controller. '
                            'Is it started?')
            return

        # Get list of methods exposed by the Master Controllers RPC interface.
        exposed_methods = [m.replace('exposed_', '', 1)
                           for m in dir(conn.root) if
                           m.startswith('exposed_') and
                           'get_service_aliases' not in m and
                           'get_service_name' not in m]

        # Build list of commands to expose.
        commands = [
            dict(command='get_current_state', alias='st'),
            dict(command='online', alias='on'),
            dict(command='capability', args='[name] [type]', alias='cap'),
            dict(command='offline', alias='off'),
            dict(command='shutdown', alias='s'),
            dict(command='exit', alias='x', local=True)
        ]

        for command in commands:
            if command.get('local', False):
                continue
            if command['command'] not in exposed_methods:
                self._log.critical('Command "{}" not exposed by the MC RPC '
                                   'interface'.format(command['command']))
                return

        _args = []
        steps = [
                    ('get_current_state', None, []),
                    ('online', 'Available', []),
                    ('capability', None, ['receiver', 'vis_receive'],
                        self.run_vis, ('sip/etc/vis_sender_config.json')),
                    ('capability', None, ['receiver', 'vis_receive'],
                        self.vis_timeout),
                    ('offline', 'Standby', []),
                    ('shutdown', None, [])
                ]

        for step in steps:
            function = getattr(conn.root, step[0])
            ret = function(*step[2])
            print('>> ', step[0],':', ret)

            if len(step) > 3:
                if len(step) > 4:
                    step[3](step[4])
                else:
                    step[3]()

            if step[1] is not None:
                count = 0
                while not ret == step[1]:
                    if count == 10:
                        print('Encountered error in [', step[0], '], terminating')
                        return -1
                    count += 1;
                    function = getattr(conn.root, 'get_current_state')
                    _args = []
                    ret = function(*_args)
                    print('\t>> get_current_state:', ret)
                    time.sleep(1)

    def _init_master(self):
        print('Starting master controller, waiting to initialise...')
        self._master = subprocess.Popen(['/usr/bin/python', '-m', 'sip.master'],
                stdin=subprocess.PIPE,stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)

        self.poller = select.poll()
        self.poller.register(self._master.stdout,select.POLLIN)

        #TODO properly determine startup complete
        self.poll_master_stdout(5, '** Enter command:', '_init_master')
   
    def shutdown_master(self):
        print('Waiting for master to shut down.')
        #self.poll_master_stdout(5, 'Shutdown complete. Goodbye!', 'shutdown_master')
        self.poll_master_stdout(5, 'SIGINT', 'shutdown_master')

        self._master.wait()
        final_msgs = self._master.communicate()
        #TODO print?
        if DEBUG:
            print(final_msgs)

    def run_vis(self, config):
        self.poll_master_stdout(5, 'Waiting to receive', 'run_vis initialisation')

        proc = subprocess.Popen(['/usr/bin/python', '-m',
            'sip.emulators.csp_visibility_sender', config],
                stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
        proc.wait()
        output = proc.communicate()
        if DEBUG:
            print('--------------------------\nvis_sender, stdout:\n--------------------------')
            print(output[0].decode("utf-8"))
            print('--------------------------\nvis_sender, stderr:\n--------------------------')
            print(output[1].decode("utf-8"))

        self.poll_master_stdout(5, 'Received heap 9', 'run_vis termination')

    def vis_timeout(self):
        self.poll_master_stdout(60, 'vis_receiver_task.py timed out',
        'vis_timeout')

    def poll_master_stdout(self, timeout, trigger, errstring):

        output = ''
        timer = 0

        while timer < timeout and output.find(trigger) is -1:
            time.sleep(1)
            timer += 1
            if not self.poller.poll(0):
                pass
            else:
                # Yes, we have to peek AND read... peek to get size, read to
                # actually advance the buffer.
                # Seeking is not supported by Popen.stdout...
                outsize = len(self._master.stdout.peek())
                output = self._master.stdout.read(outsize).decode("utf-8")
                if DEBUG:
                    print(errstring + ' loop:' + str(outsize))
                    print(output)
                    print('---------------------- ' + str(timer))


        if timer is timeout:
            print('error in ' + errstring)
            print('pos: ' + str(output.find(trigger)))


if __name__ == '__main__':


    #master = subprocess.run(args=['/usr/bin/python', '-m', 'sip.master'])


    runner = TestSipRunner()
    runner.test_master_rpc()
    runner.shutdown_master()

