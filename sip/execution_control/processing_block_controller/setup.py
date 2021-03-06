"""Setup config file to package SIP Processing BLock Controller library."""
from setuptools import setup
from sip_pbc.release import __version__


with open('README.md', 'r') as file:
    LONG_DESCRIPTION = file.read()


setup(name='skasip-pbc',
      version=__version__,
      author='SKA SDP SIP team.',
      description='SIP Processing Block Controller library.',
      long_description=LONG_DESCRIPTION,
      long_description_content_type='text/markdown',
      url='https://github.com/SKA-ScienceDataProcessor/integration-prototype'
          '/tree/master/sip/execution_control/processing_block_controller',
      packages=['sip_pbc'],
      install_requires=[
          'skasip-config-db>=1.2.2',
          'skasip-docker-swarm>=1.0.10',
          'skasip-logging>=1.0.14',
          'redis==2.10.6',
          'jinja2>=2.10.1',
          'celery==4.2.1',
          'PyYAML==4.2b4'
      ],
      zip_safe=False,
      classifiers=[
          "Programming Language :: Python :: 3 :: Only",
          "Development Status :: 1 - Planning",
          "License :: OSI Approved :: BSD License"
      ]
      )
