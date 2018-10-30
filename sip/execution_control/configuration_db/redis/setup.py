"""Setup config file to package the configuration database."""
from setuptools import setup

setup(name='skasip-config_db',
      version='0.4.0',
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
