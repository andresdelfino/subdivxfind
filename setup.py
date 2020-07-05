#!/usr/bin/env python

from setuptools import setup


setup(
    name='subdivxfind',
    version='1.0',
    packages=[
        'subdivxfind',
    ],
    install_requires=[
        'bs4',
        'html5lib',
        'requests',
    ],
    entry_points={
        'console_scripts': [
            'subdivxfind = subdivxfind:main',
        ],
    }
)
