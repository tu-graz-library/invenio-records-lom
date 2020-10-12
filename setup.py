# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""invenio data model for Learning object metadata"""

import os
from setuptools import find_packages, setup
readme = open('README.rst').read()
history = open('CHANGES.rst').read()

tests_require = [
    'check-manifest>=0.25',
    'coverage>=4.0',
    'isort>=4.3.3',
    'pydocstyle>=1.0.0',
    'pytest-cache>=1.0',
    'pytest-cov>=1.8.0',
    'pytest-pep8>=1.0.6',
    'pytest>=2.8.0',
    'pytest-invenio>=1.0.1',
    'invenio-app>=1.0.1',
    'redis>=2.10.6'
]

invenio_search_version = '1.0.0'
invenio_db_version = '1.0.1'

extras_require = {
    'docs': [
        'Sphinx>=1.5.1',
    ],
    # Elasticsearch version
    'elasticsearch7': [
        'invenio-search[elasticsearch7]>={}'.format(invenio_search_version),
    ],
    # Databases
    'mysql': [
        'invenio-db[mysql]>={}'.format(invenio_db_version),
    ],
    'postgresql': [
        'invenio-db[postgresql]>={}'.format(invenio_db_version),
    ],
    'tests': tests_require,
}

extras_require['all'] = []
for name, reqs in extras_require.items():
    if name[0] == ':' or name in ('elasticsearch7', 'mysql', 'postgresql'):
        continue
    extras_require['all'].extend(reqs)

setup_requires = [
    'Babel>=1.3',
    'pytest-runner>=2.6.2',
]

install_requires = [
    'arrow>=0.13.0',
    'CairoSVG>=1.0.20',
    'edtf>=4.0.1',
    'Faker>=2.0.3',
    'Flask-BabelEx>=0.9.4',
    'idutils>=1.1.7',
    'invenio-assets>=1.2.2',
    'invenio-communities>=2.0.4',
    'invenio-drafts-resources>=0.1.3',
    'invenio-formatter[badges]>=1.1.0a1',
    'invenio-jsonschemas>=1.1.0',
    'invenio-pidstore>=1.2.1',
    'invenio-records-rest>=1.7.1',
    'invenio-records>=1.3.2',
    'invenio-records-files>=1.2.1',
    'invenio-records-permissions>=0.9.0',
    'invenio-records-resources>=0.3.2',
    'invenio-records-ui>=1.2.0a1',
    'invenio-previewer>=1.2.1',
    'marshmallow>=3.3.0'
    'pycountry>=18.12.8',
    'six>=1.12.0'  # Needed to pass CI tests
]

packages = find_packages()


# Get the version string. Cannot be done with import!
g = {}
with open(os.path.join('invenio_records_lom', 'version.py'), 'rt') as fp:
    exec(fp.read(), g)
    version = g['__version__']

setup(
    name='invenio_records_lom',
    version=version,
    description=__doc__,
    long_description=readme,
    keywords='invenio_records_lom Invenio',
    license='MIT',
    author='Graz University of Technology',
    author_email='info@tugraz.at',
    url='https://github.com/tu-graz-library/invenio-records-lom/',
    packages=packages,
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    entry_points={
        'invenio_base.apps': [
            'invenio_records_lom = invenio_records_lom:invenio_records_lom',
        ],
        'invenio_base.api_apps': [
            'invenio_records_lom = invenio_records_lom:invenio_records_lom',
        ],
        # 'invenio_base.api_blueprints':
        #     'dm_api = invenio_app_rdm.theme.views:dm_record_bp',
        # ],
        'invenio_base.blueprints': [
            'invenio_records_lom = invenio_records_lom.views:blueprint',
        ],
        'invenio_jsonschemas.schemas': [
            'invenio_records_lom = invenio_records_lom.jsonschemas'
        ],
        'invenio_search.mappings': [
            'dmrec = invenio_records_lom.mappings',
            # 'dmdrafts = invenio_rdm_records.mappings.drafts',
        ],
    },
    extras_require=extras_require,
    install_requires=install_requires,
    setup_requires=setup_requires,
    tests_require=tests_require,
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Development Status :: 3 - Planning',
    ],
)
