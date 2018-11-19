# coding: utf-8
"""Setup config file to package the configuration database."""
from os import walk, listdir
from os.path import join
from setuptools import setup
import sip_config_db


def package_files(directory):
    """Get list of data files to add to the package."""
    paths = []
    for (path, _, file_names) in walk(directory):
        for filename in file_names:
            paths.append(join('..', path, filename))
    return paths


DATA = package_files(join('sip_config_db', 'data'))
TEST_DATA = package_files(join('sip_config_db', 'tests', 'data'))
SCHEMA = package_files(join('sip_config_db', 'scheduling', 'schema'))

SCRIPTS_DIR = join('sip_config_db', 'scripts')
SCRIPTS = [join(SCRIPTS_DIR, file) for file in listdir(SCRIPTS_DIR)]

with open('README.md', 'r') as file:
    LONG_DESCRIPTION = file.read()

VERSION = sip_config_db.__version__


setup(name='skasip_config_db',
      version=VERSION,
      author='SKA SDP SIP team.',
      description='SIP Execution Control Configuration Database library.',
      long_description=LONG_DESCRIPTION,
      long_description_content_type='text/markdown',
      url='https://github.com/SKA-ScienceDataProcessor/integration-prototype'
          '/tree/master/sip/execution_control/configuration_db',
      packages=[
          'sip_config_db',
          'sip_config_db/_events',
          'sip_config_db/scheduling',
          'sip_config_db/states',
          'sip_config_db/utils'
      ],
      scripts=SCRIPTS,
      package_data={'': DATA + TEST_DATA + SCHEMA},
      include_package_data=True,
      install_requires=[
          'redis==2.10.6',
          'jsonschema==2.6.0',
          'jinja2==2.10',
          'PyYaml==3.13'
      ],
      zip_safe=False,
      classifiers=[
          "Programming Language :: Python :: 3 :: Only",
          "Development Status :: 1 - Planning",
          "License :: OSI Approved :: BSD License"
      ]
      )
