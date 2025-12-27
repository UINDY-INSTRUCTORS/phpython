#!/usr/bin/env python
"""Lean setup for phpython distribution."""

from setuptools import setup, find_packages

setup(
    name='phpython',
    version='0.1.0',
    description='A unified abstraction layer for CircuitPython and MicroPython',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Steve',
    author_email='steve@spvi.com',
    license='MIT',
    packages=find_packages(exclude=['tests', '*.tests', '*.tests.*', 'tests.*']),
    python_requires='>=3.4',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Education',
        'Programming Language :: Python :: 3',
        'Topic :: Education',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
