#!/usr/bin/env python
from setuptools import setup
from setuptools.command.install import install
import os

class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        os.system('adduser --home /var/lib/sfmserver --gecos "" sfmserver')
        install.run(self)



setup(
    name='sfmserver',
    
    version='1.0.0',
    description='SSH forward manager server package',

    url='githuburl',

    author='N0xx',
    author_email='n0xx@protonmail.com',

    cmdclass={
        'install': PostInstallCommand,
    },
    packages=['sfmserver'],
    data_files=[('/etc/systemd/system/',['conf/sfmserver.service'])],
    entry_points = {
        'console_scripts': [
            'sfmserver = sfmserver.main:main',
            'sfmserverctl = sfmserver.serverctl:main'
        ],              
    },
)
