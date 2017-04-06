""" Apache Spark Platform-as-a-Service interface

.. moduleauthor:: Arjen Tamerus <at748@cam.ac.uk>
"""

from sip.common.paas import PaaS, TaskDescriptor, TaskStatus

class SparkPaas(Paas):
    def __init__(self):
        pass

    def run_task(self, name, task, ports, args):
        pass

    def run_service(self, name, task, ports, args):
        pass

    def find_task(self, name):
        pass

class SparkTaskDescriptor(TaskDescriptor):
    def __init__(self, name):
        pass

    def delete(self):
        pass

    def status(self):
        pass

    def location(self):
        pass
