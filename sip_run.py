# -*- coding: utf-8 -*-
"""Script to that can be used to run SIP modules.

Current modules:
- Master Controller
- Master Controller RPC interface.
- CSP visibility emulator
"""
import argparse
import logging
import sys
import simplejson as json
import os
import rpyc


class SipRunner(object):
    """Class to run SIP modules.

    Modules are registered into this class by defining a 'run_{module}' method.
    """

    def __init__(self):
        """Sets up a command line parser, initialises logging and runs the
        specified module.
        """
        # Set up command line parser.
        run_methods = [func[4:] for func in dir(__class__)
                       if callable(getattr(__class__, func))
                       and func.startswith('run_')]
        parser = argparse.ArgumentParser(prog='sip_run.py',
                                         description='Run a SIP function.')
        parser.add_argument('module', help='Module to run.',
                            choices=run_methods)
        parser.add_argument('-v', '--verbose', help='Enable verbose messages.',
                            action='store_true')
        parser.add_argument('--config', '-c', type=argparse.FileType('r'),
                            help='JSON configuration file.')
        self.args = parser.parse_args()

        # Initialise logging.
        self._log = self._init_logger()

        # Run the specified module.
        self._dispatch(self.args.module)

    @staticmethod
    def run_master():
        """Run the master controller."""
        print('Running master...')
        os.environ['SIP_HOSTNAME'] = os.uname()[1]
        sys.path.append(os.path.join(os.path.dirname(__file__), 'common'))
        sys.path.append(os.path.join(os.path.dirname(__file__), 'master'))
        from master.sip_master.main import main as master_main
        resources = os.path.join('master', 'etc', 'resources.json')
        slave_map = os.path.join('master', 'etc', 'slave_map.json')
        master_main(slave_map, resources)

    def run_master_rpc(self):
        """Method to talk to the RPC interface to the master controller."""

        def _is_int(value):
            """Return true if the specified value is an int."""
            try:
                int(value)
                return True
            except ValueError:
                return False

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
        # print(exposed_methods)
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

        def _print_commands():
            """Print allowed commands."""
            print('Allowed commands:')
            for i, cmd in enumerate(commands):
                _alias = ''
                _args = ''
                if 'alias' in cmd and cmd['alias'] is not None:
                    _alias = '({})'.format(cmd['alias'])
                if 'args' in cmd and cmd['args'] is not None:
                    _args = '{}'.format(cmd['args'])

                print('  {}. {} {} {}'.format(i, cmd['command'], _args, _alias))

        # While responding to command line input.
        while True:
            _input = input('?').split()

            # If no input is specified print the list of options.
            if not _input:
                _print_commands()
                continue

            # Extract the command and arguments from the input and convert
            # int to command name
            _command = _input[0]
            _args = _input[1:]
            if _is_int(_command):
                try:
                    _command = commands[int(_command)]['command']
                except IndexError:
                    _print_commands()
                    continue

            # Fail if the command is unknown.
            _ok = False
            for command in commands:
                if _command == command['command']:
                    _ok = True
                    break
                elif _command == command['alias']:
                    _command = command['command']
                    _ok = True
                    break
            if not _ok:
                self._log.error('Unknown command: "{}"'.format(_command))
                _print_commands()
                continue

            if _command == 'exit' or _command == 'x':
                break
            else:
                function = getattr(conn.root, _command)
                ret = ''
                try:
                    ret = function(*_args)
                except TypeError as error:
                    print('Error: ', error)
                if not _args:
                    print('>> Issued command: {}()'.format(_command))
                else:
                    print('>> Issued command: {}({})'.format(_command,
                                                             ', '.join(_args)))
                print('>> Return:', ret)
                if _command == 'shutdown' and ret != 'rejected':
                    break

    def run_csp_vis_sender(self):
        """Run the visibility (SPEAD) data emulator / sender"""
        import emulators.csp_visibility_sender.__main__
        if self.args.config is not None:
            self._log.info('Loading config: {}'.format(self.args.config.name))
            config = json.load(self.args.config)
            emulators.csp_visibility_sender.__main__.main(config, self._log)
        else:
            print('ERROR: Unable to run {}, configuration required.'
                  .format(self.args.module))

    def _dispatch(self, value):
        """Dispatch (execute) a run_{} method."""
        method_name = 'run_' + str(value)
        try:
            method = getattr(self, method_name)
        except AttributeError:
            print(method_name, 'not found.')
        else:
            method()

    def _init_logger(self):
        """Initialise python logging object."""
        log = logging.getLogger(__file__)
        level = logging.DEBUG if self.args.verbose else logging.INFO
        log.setLevel(level)
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(level)
        formatter = logging.Formatter('%(levelname)s | %(message)s')
        ch.setFormatter(formatter)
        log.addHandler(ch)
        return log


if __name__ == '__main__':
    SipRunner()
