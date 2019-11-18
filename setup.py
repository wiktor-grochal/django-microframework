#!/usr/bin/env python

from setuptools import find_packages, setup


def read(f):
    return open(f, 'r', encoding='utf-8').read()


setup(
    name='django-microframework',
    description=(
        'Django microframework allows you for easy synchronization '
        'of database entities between multiple django instances.'
    ),
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    version='0.1.0',
    author='Wiktor Grochal',
    author_email='wiktor.grochal@gmail.com',
    url='https://github.com/wiktor-grochal/django-microframework',
    license='BSD',
    packages=find_packages(),
    include_package_data=True,
    install_requires=['django', 'python-dateutil', 'nameko'],
    python_requires=">=3.6",
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Framework :: Django :: 2.1',
        'Framework :: Django :: 2.2',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        'Topic :: Utilities',
    ],
)