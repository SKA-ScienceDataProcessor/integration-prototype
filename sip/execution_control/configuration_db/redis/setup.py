"""Setup config file to package configuration database."""
from setuptools import setup

setup(name='skasip-config_db',
      version='0.1',
      description='SIP Execution Control Configuration Database '
                  'client library.',
      author='SKA SIP',
      packages=['config_db'],
      install_requires=[
          'redis',
          'jsonschema',
          'simplejson',
          'namesgenerator'],
      zip_safe=False)
