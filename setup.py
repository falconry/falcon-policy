#!/usr/bin/env python

from setuptools import setup, find_packages

desc = ''
with open('README.rst') as f:
    desc = f.read()

setup(
    name='falcon-policy',
    version='0.1.0',
    description=('Policy middleware for Falcon APIs'),
    long_description=desc,
    url='https://github.com/falconry/falcon-policy',
    author='John Vrbanac',
    author_email='john.vrbanac@linux.com',
    license='Apache v2',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    keywords='falcon middleware policy rbac role based access',
    packages=find_packages(exclude=['contrib', 'docs', 'test*']),
    install_requires=[
        'falcon',
        'six',
    ],
    package_data={},
    data_files=[],
    entry_points={
        'console_scripts': [],
    },
)
