# coding: utf-8
"""Setup config file to package the configuration database."""
import os
from setuptools import setup


def package_files(directory):
    """Get list of data files to add to the package."""
    paths = []
    for (path, _, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths


DATA_FILES = package_files('config_db/utils/data')
SCHEMA_FILES = package_files('config_db/schema')


setup(name='skasip_config_db',
      version='1.0.0',
      description='SIP Execution Control Configuration Database '
                  'client library.',
      author='SKA SIP',
      packages=['config_db', 'config_db/utils'],
      # scripts=['config_db/scripts/skasip_initialise_database'],
      package_data={'': DATA_FILES + SCHEMA_FILES},
      include_package_data=True,
      install_requires=['redis', 'jsonschema'],
      zip_safe=False)
