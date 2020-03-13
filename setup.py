#!/usr/bin/env python
from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='python-currencycom',
    version='0.1.1',
    packages=['currencycom'],
    description='Currency.com REST API python implementation',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/sann05/python-currencycom',
    author='Aliaksandr Sheliutsin',
    license='MIT',
    author_email='',
    install_requires=['requests', ],
    keywords='currencycom exchange rest api bitcoin ethereum btc eth',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    python_requires='>=3.5',
)
