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


DATA = package_files('config_db/data')
TEST_DATA = package_files('config_db/tests/data')


setup(name='skasip_config_db',
      version='1.0.9',
      description='SIP Execution Control Configuration Database library.',
      author='SKA SDP SIP team',
      packages=['config_db', 'config_db/utils', 'config_db/tests'],
      scripts=['config_db/scripts/skasip_init_config_db'],
      package_data={'': DATA + TEST_DATA},
      include_package_data=True,
      install_requires=[
          'redis>=2.10.6',
          'jsonschema>=2.6.0',
          'jinja2>=2.10',
          'PyYaml>=3.13'
      ],
      zip_safe=False)
