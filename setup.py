#!/usr/bin/env python
# Copyright (c) 2018, Red Hat, Inc.
#   License: MIT
import setuptools
import re

from toolchest import __version__

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()


def requires(prefix=''):
    """Retrieve requirements from requirements.txt
    """
    try:
        reqs = map(str.strip, open(prefix + 'requirements.txt').readlines())
        reqs = filter(lambda s: re.match(r'\W', s), reqs)
        return reqs
    except Exception:
        pass
    return []


setuptools.setup(
    name='toolchest',
    version=__version__,
    install_requires=requires(),
    license='MIT',
    description=("toolchest is a collection of generic "
                 "functions for release-depot."),
    long_description=readme + '\n\n' + history,
    author='Red Hat',
    author_email='lhh@redhat.com',
    maintainer='Lon Hohberger',
    maintainer_email='lon@metamorphism.com',
    packages=['toolchest', 'toolchest.rpm'],
    url='http://github.com/release-depot/toolchest',
    data_files=[("", ["LICENSE"])],
    classifiers=['Development Status :: 4 - Beta',
                 'Intended Audience :: Developers',
                 'Natural Language :: English',
                 'Operating System :: POSIX :: Linux',
                 'Programming Language :: Python :: 3',
                 'Programming Language :: Python :: 3.4',
                 'Programming Language :: Python :: 3.5',
                 'Programming Language :: Python :: 3.6',
                 'Topic :: Software Development',
                 'Topic :: Software Development :: Libraries',
                 'Topic :: Software Development :: Libraries :: Python Modules',
                 'Topic :: Utilities'],
)
