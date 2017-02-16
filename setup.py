#!/usr/bin/env python
from numpy import get_include
from os.path import join, dirname
import platform
try:
    from setuptools import setup, Extension
    from setuptools.command.build_ext import build_ext
except ImportError:
    from distutils.core import setup, Extension
    from distutils.command.build_ext import build_ext

# Define the extension modules to build.
modules = [
    ('_test_lib', 'test_lib.c')
]


class BuildExt(build_ext):
    """Class used to build SIP Python extensions. Inherits build_ext."""

    def run(self):
        """Overridden method. Runs the build.
        Library directories and include directories are checked here, first.
        """
        # Add the numpy include directory.
        self.include_dirs.insert(0, get_include())

        # Call the base class method.
        build_ext.run(self)

    def build_extension(self, ext):
        """Overridden method. Builds each Extension."""
        ext.runtime_library_dirs = self.rpath

        # Unfortunately things don't work as they should on the Mac...
        if platform.system() == 'Darwin':
            for t in self.rpath:
                ext.extra_link_args.append('-Wl,-rpath,'+t)

        # Call the base class method.
        build_ext.build_extension(self, ext)


def get_sip_version():
    """Get the version of SIP from the version file."""
    globals_ = {}
    with open(join(dirname(__file__), 'sip', '_version.py')) as f:
        code = f.read()
    exec(code, globals_)
    return globals_['__version__']


# Call setup() with list of extensions to build.
extensions = []
for m in modules:
    extensions.append(Extension(
        'sip.ext.' + m[0], sources=[join('sip', 'ext', 'src', m[1])],
        language='c'))
setup(
    name='sip',
    version=get_sip_version(),
    description='SDP Integration Prototype',
    packages=['sip', 'sip.common', 'sip.emulators', 'sip.ext', 'sip.master',
              'sip.processor_software', 'sip.slave', 'sip.tasks'],
    ext_modules=extensions,
    classifiers=[
            'Development Status :: 3 - Alpha',
            'Environment :: Console',
            'Intended Audience :: Science/Research',
            'Topic :: Scientific/Engineering :: Astronomy',
            'License :: OSI Approved :: Apache License',
            'Operating System :: POSIX',
            'Programming Language :: C',
            'Programming Language :: Python :: 3'
    ],
    author='SDP Integration Prototype Developers',
    license='Apache',
    install_requires=['numpy'],
    setup_requires=['numpy'],
    cmdclass={'build_ext': BuildExt}
    )
