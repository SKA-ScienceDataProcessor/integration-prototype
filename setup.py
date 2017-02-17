#!/usr/bin/env python
from numpy import get_include
import os
import platform
from setuptools import setup, find_packages, Extension
from setuptools.command.build_ext import build_ext
from setuptools.command.install import install

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


class Install(install):
    """Class used to install SIP. Inherits install."""

    def run(self):
        """Overridden method. Runs the installation."""
        install.run(self)  # Call the base class method.

        # Make sure all Python tasks are executable.
        for file_path in self.get_outputs():
            if 'tasks' in file_path and '.py' in file_path:
                st = os.stat(file_path)
                os.chmod(file_path, st.st_mode | 73)


def get_sip_version():
    """Get the version of SIP from the version file."""
    globals_ = {}
    with open(os.path.join(
            os.path.dirname(__file__), 'sip', '_version.py')) as f:
        code = f.read()
    exec(code, globals_)
    return globals_['__version__']


# Call setup() with list of extensions to build.
extensions = []
for m in modules:
    extensions.append(Extension(
        'sip.ext.' + m[0], sources=[os.path.join('sip', 'ext', 'src', m[1])],
        language='c'))
setup(
    name='sip',
    version=get_sip_version(),
    description='SDP Integration Prototype',
    packages=find_packages(),
    package_data={'': ['*.json']},
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
    cmdclass={'build_ext': BuildExt, 'install': Install}
    )
