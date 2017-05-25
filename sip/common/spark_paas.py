""" Apache Spark Platform-as-a-Service interface

.. moduleauthor:: Arjen Tamerus <at748@cam.ac.uk>
"""

import subprocess
import requests
import json
import re

from sip.common.paas import Paas, TaskDescriptor, TaskStatus

class SparkPaaS(Paas):

    # Need a class variable if we want to use the same model as docker_paas...
    # TODO think would be better to just initialise a single instance instead of
    # always recreating - What if we have mulitple masters?

    # Still, keeping this for now - start with copying Docker_PaaS behaviour for
    # slave management, easy to adjust later on.

    spark_master = None
    #spark_master = {
    #    'protocol': 'spark',
    #    'url': '127.0.0.1',
    #    'port': '7077',
    #    'master_port': '8080',
    #    'history_server': '127.0.0.1',
    #    'history_port': '18080'
    #    }
    tasks = {}

    def __init__(self):
        # worker port is set at worker start, so has to be read at app start
        if not SparkPaaS.spark_master:
            #print('setting SparkPaaS.spark_master')
            SparkPaaS.spark_master = {
                    'protocol': 'spark',
                    'url': '127.0.0.1',
                    'port': '7077',
                    'master_port': '8080',
                    'history_server': '127.0.0.1',
                    'history_port': '18080'
                    }
        self.spark_master = SparkPaaS.spark_master
        self.tasks = SparkPaaS.tasks

    def run_task(self, name, task, ports=None, args=None):
        if name in self.tasks.keys():
            return None #TODO apparently we remove and overwrite, or something?
        td = SparkTaskDescriptor(name, self.spark_master)
        self.tasks[name] = td

        cmd = self.task_to_command(args) # TODO
        app = subprocess.Popen(cmd, stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE, shell=True)

        ui_address = None
        ui_port = None
        application_id = None

        while application_id is None:
            line = str(app.stderr.readline(), 'utf-8')
            if len(line) is 0:
                #TODO cleanup correctly
                break

            ## Get worker UI address for status ping
            #if ui_address is None:
            #    if line.find('Started ServerConnector') > -1:
            #        # Stole ip:port regex http://stackoverflow.com/a/23542162
            #        match = re.search('[0-9]+(?:\.[0-9]+){3}:[0-9]+', line)

            #        if match:
            #            ui_address, ui_port = match.group(0).split(':')

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
        #if task is None:
        #    args = '--conf spark.eventLog.enabled=true --conf spark.eventLog.dir=file:///tmp/spark-events --executor-memory 2g --driver-memory 2g --total-executor-cores 2'
        #    cmd = 'spark-submit --master {protocol}://{host}:{port} {arguments} {jarpath}/{jarfile}'.format(
        #            protocol=self.spark_master['protocol'],
        #            host=self.spark_master['url'],
        #            port=self.spark_master['port'],
        #            arguments=args,
        #            jarpath='/usr/local/bin',
        #            jarfile='sdp-pipeline_2.10-1.0.jar'
        #        )

        #    #print(cmd)
        #    return cmd

        #print(task)

        cmd = 'spark-submit --master {protocol}://{host}:{port} {arguments} {jarpath}/{jarfile}'.format(
                protocol=self.spark_master['protocol'],
                host=self.spark_master['url'],
                port=self.spark_master['port'],
                arguments=task['spark_args'],
                jarpath=task['jarpath'],
                jarfile=task['jarfile']
            )

        return cmd

    def run_service(self, name, task, ports=None, args=None):
        # Not sure if / don't think we need this one
        self.delete_task(name)
        return self.run_task(name, task, ports, args)

    def find_task(self, name):
        if name in self.tasks.keys():
            return self.tasks[name]

        return None

    def delete_task(self, name):
        task = self.find_task(name)

        #print('delete_task')

        if task:
            task.delete()
            del self.tasks[name]
            return True

        return False

class SparkTaskDescriptor(TaskDescriptor):
    def __init__(self, name, master_config):
        self.spark_master = master_config
        self.name = name
        #self.task_mode = 'app' # TODO or 'driver', and don't use strings

        self.ui_address = None
        self.ui_port = None
        self.application_id = None # app-14x-4x OR driver-14x-4x

    def delete(self):
        #print('delete')
        status = self.status()
        if status is not TaskStatus.EXITED:
            self.kill()

    def kill(self):
        # Killing apps is not supported in YARN
        pass

    def status(self):
        # Current situation: extract worker address at task start, try
        # connecting there for faster status update. Otherwise try to connect to
        # history server.

        # TODO Due to delay in history server status value can be unreliable,
        # particularly for short jobs - might go from RUNNING back to STARTING
        # (4040 to 18080 switchover happening before history server updated)

        #if self.application_id is None:
        #    return TaskStatus.UNKNOWN

        #rest_url = 'http://{url}:{port}/api/v1/applications/{appid}'

        #try:
        #    req = requests.get(
        #            rest_url.format(
        #                url=self.ui_address,
        #                port=self.ui_port,
        #                appid=self.application_id
        #            )
        #        )
        #except:
        #    try:
        #        req = requests.get(
        #                rest_url.format(
        #                    url=self.spark_master['history_server'],
        #                    port=self.spark_master['history_port'],
        #                    appid=self.application_id
        #                )
        #            )
        #    except:
        #        return TaskStatus.ERROR

        #if not req.ok or req.status_code != 200:
        #    return TaskStatus.STARTING

        #if req.headers['Content-Type'] != 'application/json':
        #    return TaskStatus.UNKNOWN

        #resp = req.json()

        #if 'attempts' in resp.keys():
        #    for attempt in resp['attempts']:
        #        if 'completed' in attempt.keys():
        #            if attempt['completed'] is True:
        #                return TaskStatus.EXITED
        #            else:
        #                return TaskStatus.RUNNING
        #            break

        #    return TaskStatus.UNKNOWN

        #return TaskStatus.UNKNOWN

        # ALT: Use only Spark master JSON ui

        if self.application_id is None:
            return TaskStatus.ERROR

        rest_url = 'http://{url}:{port}/json'.format(
                url=self.spark_master['url'],
                port=self.spark_master['master_port']
                )

        try:
            req = requests.get(rest_url)
        except:
            return TaskStatus.ERROR

        if not req.ok or req.status_code != 200:
            return TaskStatus.ERROR

        resp = req.json()

        if 'activeapps' not in resp.keys() or 'completedapps' not in resp.keys():
            return TaskStatus.ERROR

        for app in resp['activeapps']:
            if app['id'] == self.application_id:
                return TaskStatus.RUNNING

        for app in reversed(resp['completedapps']):
            if app['id'] == self.application_id:
                return TaskStatus.EXITED

        return TaskStatus.UNKNOWN

    def location(self):
        pass

    def set_app_config(self, app_id, addr, port):
        self.application_id = app_id
        self.ui_address = addr
        self.ui_port = port

