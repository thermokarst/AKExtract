# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='SNAPExtract',
    version='0.1.0',
    description='Extract climate data from SNAP datasets',
    long_description=readme,
    author='Matthew Ryan Dillon',
    author_email='matthewrdillon@gmail.com',
    url='https://github.com/thermokarst/snapextract',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)
