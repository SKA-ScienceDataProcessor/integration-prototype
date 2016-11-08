# -*- coding: utf-8 -*-
"""Script to run SIP modules."""
import argparse
import logging
import sys
import simplejson as json
import emulators.csp_visibility_sender.__main__
import os


class SipRunner(object):
    """Class to run SIP modules.

    SIP modules are defined by the existence of a 'run_{module}' method
    of this class.
    """

    def __init__(self):
        """Constructor."""
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
        # Configure logging.
        self.log = logging.getLogger(__file__)
        level = logging.DEBUG if self.args.verbose else logging.INFO
        self.log.setLevel(level)
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(level)
        formatter = logging.Formatter('%(asctime)s: %(message)s',
                                      '%Y/%m/%d-%H:%M:%S')
        ch.setFormatter(formatter)
        self.log.addHandler(ch)
        self.dispatch(self.args.module)

    @staticmethod
    def run_master():
        """Run the master controller"""
        print('Running master...')
        os.environ['SIP_HOSTNAME'] = os.uname()[1]
        sys.path.append(os.path.join(os.path.dirname(__file__), 'common'))
        sys.path.append(os.path.join(os.path.dirname(__file__), 'master'))
        from master.sip_master.main import main as master_main
        resources = os.path.join('master', 'etc', 'resources.json')
        slave_map = os.path.join('master', 'etc', 'slave_map.json')
        master_main(slave_map, resources)

    @staticmethod
    def run_slave():
        print('Running slave...')
        sys.path.append(os.path.join(os.path.dirname(__file__), 'common'))
        sys.path.append(os.path.join(os.path.dirname(__file__), 'slave'))
        config = {'name': 'slave1',
                  'heartbeat_port': 2000,
                  'server_port': 2001,
                  'logging_address': '127.0.0.1',
                  'task_control_module': 'task_control'}
        import signal
        signal.signal(signal.SIGTERM, lambda: sys.exit(0))
        os.environ['SIP_HOSTNAME'] = config['logging_address']
        from sip_slave.main import main as slave_main
        slave_main(config['name'], config['heartbeat_port'],
                   config['server_port'], config['task_control_module'])

    def run_csp_vis_sender(self):
        """Run the visibility (SPEAD) data emulator / sender"""
        if self.args.config is not None:
            self.log.info('Loading config: {}'.format(self.args.config.name))
            config = json.load(self.args.config)
            emulators.csp_visibility_sender.__main__.main(config, self.log)
        else:
            print('ERROR: Unable to run {}, configuration required.'
                  .format(self.args.module))

    def dispatch(self, value):
        """Dispatch a run method."""
        method_name = 'run_' + str(value)
        try:
            method = getattr(self, method_name)
        except AttributeError:
            print(method_name, 'not found.')
        else:
            method()


if __name__ == '__main__':
    SipRunner()
