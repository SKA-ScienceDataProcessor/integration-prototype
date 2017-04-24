""" Apache Spark Platform-as-a-Service interface

.. moduleauthor:: Arjen Tamerus <at748@cam.ac.uk>
"""

import subprocess
import requests
import json
import re

from sip.common.paas import Paas, TaskDescriptor, TaskStatus

class SparkPaas(Paas):
    def __init__(self):
        # worker port is set at worker start, so has to be read at app start
        self.spark_master = {
                'protocol': 'spark',
                'url': '127.0.0.1',
                'port': '7077',
                'history_server': '127.0.0.1',
                'history_port': '18080'
                }
        self.tasks = {}

    def run_task(self, name, task, ports=None, args=None):
        #TODO What are the expected retvals?
        if name in self.tasks.keys():
            return None #TODO apparently we remove and overwrite, or something?
        td = SparkTaskDescriptor(name, self.spark_master) # Or however it's done. Look at docker_paas
        self.tasks[name] = td

        cmd = self.task_to_command(task) # TODO
        app = subprocess.Popen(cmd, stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE, shell=True) # can we do without shell?

        ui_address = None
        ui_port = None
        application_id = None

        while application_id is None:
            line = str(app.stderr.readline(), 'utf-8')
            if len(line) is 0:
                #TODO cleanup correctly
                break

            # Get worker UI address for status ping
            if ui_address is None:
                if line.find('Started ServerConnector') > -1:
                    # Stole ip:port regex http://stackoverflow.com/a/23542162
                    match = re.search('[0-9]+(?:\.[0-9]+){3}:[0-9]+', line)

                    if match:
                        ui_address, ui_port = match.group(0).split(':')

            # Extract app ID
            else:
                match = re.search('app-[0-9]{14}-[0-9]{4}', line)

                if match:
                    application_id = match.group(0)

        # Close stderr pipe, otherwise subprocess hangs / requires all output
        # to be extracted before terminating. Bad.
        app.stderr.close()

        if not application_id:
            #TODO cleanup
            return None
       
        # Store essential data in task descriptor
        td.set_app_config(application_id, ui_address, ui_port)

        return td

    def task_to_command(self, task):
        args = '--conf spark.eventLog.enabled=true --conf spark.eventLog.dir=file:///tmp/spark-events --executor-memory 2g --driver-memory 2g --total-executor-cores 2'
        cmd = 'spark-submit --master {protocol}://{host}:{port} {arguments} {jarpath}/{jarfile}'.format(
                protocol=self.spark_master['protocol'],
                host=self.spark_master['url'],
                port=self.spark_master['port'],
                arguments=args,
                jarpath='/usr/local/bin',
                jarfile='sdp-pipeline_2.10-1.0.jar'
            )

        print(cmd)
        return cmd

    def run_service(self, name, task, ports=None, args=None):
        # Not sure if / don't think we need this one
        return self.run_task(name, task, ports, args)

    def find_task(self, name):
        if name in self.tasks.keys():
            return self.tasks[name]

        return None

class SparkTaskDescriptor(TaskDescriptor):
    def __init__(self, name, master_config):
        self.spark_master = master_config
        self.name = name
        self.state = TaskStatus.UNKNOWN
        self.task_mode = 'app' # TODO or 'driver', and don't use strings

        self.ui_address = None
        self.ui_port = None
        self.application_id = None # app-14x-4x OR driver-14x-4x

    def delete(self):
        # TODO send kill command(if necessary), verify, return?
        pass

    def status(self):
        # TODO when do we return TaskStatus.ERROR?

        # Current situation: extract worker address at task start, try
        # connecting there for faster status update. Otherwise try to connect to
        # history server.

        if self.application_id is None:
            return TaskStatus.UNKNOWN

        rest_url = 'http://{url}:{port}/api/v1/applications/{appid}'

        try:
            req = requests.get(
                    rest_url.format(
                        url=self.ui_address,
                        port=self.ui_port,
                        appid=self.application_id
                    )
                )
        except:
            try:
                req = requests.get(
                        rest_url.format(
                            url=self.spark_master['history_server'],
                            port=self.spark_master['history_port'],
                            appid=self.application_id
                        )
                    )
            except:
                return TaskStatus.ERROR

        if not req.ok or req.status_code != 200:
            return TaskStatus.STARTING

        if req.headers['Content-Type'] != 'application/json':
            return TaskStatus.UNKNOWN

        resp = req.json()

        if 'attempts' in resp.keys():
            for attempt in resp['attempts']:
                if 'completed' in attempt.keys():
                    if attempt['completed'] is True:
                        return TaskStatus.EXITED
                    else:
                        return TaskStatus.RUNNING
                    break

            return TaskStatus.UNKNOWN

        return TaskStatus.UNKNOWN

    def location(self):
        pass

    def set_app_config(self, app_id, addr, port):
        self.application_id = app_id
        self.ui_address = addr
        self.ui_port = port
        #TODO remove
        print(self.application_id)
        print(self.ui_address)
        print(self.ui_port)

