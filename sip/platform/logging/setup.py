# coding: utf-8
"""Setup script for the SIP logging libary."""
import setuptools


with open('README.md', 'r') as file:
    LONG_DESCRIPTION = file.read()


setuptools.setup(
    name='skasip_logging',
    version='1.0.2',
    author='SKA SDP SIP team.',
    description="SIP logging module.",
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    url='https://github.com/SKA-ScienceDataProcessor/integration-prototype'
        '/tree/master/sip/execution_control/logging',
    packages=['sip_logging'],
    classifiers=[
        "Programming Language :: Python :: 3 :: Only",
        "Development Status :: 1 - Planning",
        "License :: OSI Approved :: BSD License"
    ]
)
