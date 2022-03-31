# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""invenio data model for Learning object metadata"""

import os

from setuptools import find_packages, setup

readme = open("README.rst").read()
history = open("CHANGES.rst").read()

# Should follow inveniosoftware/invenio versions
invenio_db_version = ">=1.0.11,<1.1.0"
invenio_search_version = ">=1.4.2,<1.5.0"

tests_require = [
    "elasticsearch-dsl>=7.4.0,<8.0.0",
    "invenio-app>=1.3.3,<2.0.0",
    "pytest-invenio>=1.4.3",
    "pytest-mock>=1.6.0",
]

extras_require = {
    "docs": [
        "Sphinx>=4.2.0",
    ],
    # Elasticsearch version
    "elasticsearch7": [
        "invenio-search[elasticsearch7]{}".format(invenio_search_version),
    ],
    # Database
    "postgresql": [
        "invenio-db[postgresql,versioning]{}".format(invenio_db_version),
    ],
    "tests": tests_require,
}

extras_require["all"] = []
for name, reqs in extras_require.items():
    if name[0] == ":" or name in ("elasticsearch7", "postgresql"):
        continue
    extras_require["all"].extend(reqs)

setup_requires = [
    "Babel>=2.9, <3",
    "pytest-runner>=3.0.0,<5",
]

install_requires = [
    "invenio-jsonschemas>=1.1.3",
    "invenio-previewer>=1.3.4",
    "invenio-records-rest>=1.8.0",
    "invenio-rdm-records>=0.34.7,<0.35",
    # TODO: Prevent build fail remove after it is fixed in base module
    "jinja2<3.1",
    "click<=8.0.4",
    "Flask<2.1.0",
    "Werkzeug<=2.0.3",
]

packages = find_packages()


# Get the version string. Cannot be done with import!
g = {}
with open(os.path.join("invenio_records_lom", "version.py"), "rt") as fp:
    exec(fp.read(), g)
    version = g["__version__"]

setup(
    name="invenio_records_lom",
    version=version,
    description=__doc__,
    long_description=readme,
    keywords="invenio_records_lom Invenio lom Learning object metadata records",
    license="MIT",
    author="Graz University of Technology",
    author_email="mb_wali@hotmail.com",
    url="https://github.com/tu-graz-library/invenio-records-lom/",
    packages=packages,
    zip_safe=False,
    include_package_data=True,
    platforms="any",
    entry_points={
        "flask.commands": [
            "lom = invenio_records_lom.cli:lom",
        ],
        "invenio_base.apps": [
            "invenio_records_lom = invenio_records_lom:InvenioRecordsLOM",
        ],
        # TODO: pluck all things API
        "invenio_base.api_apps": [
            "invenio_records_lom = invenio_records_lom:InvenioRecordsLOM",
        ],
        "invenio_base.blueprints": [
            "invenio_records_lom_ui = invenio_records_lom.ui:create_blueprint",
            "invenio_records_lom_resource_registerer = invenio_records_lom.views:blueprint",
        ],
        "invenio_base.api_blueprints": [
            "invenio_records_lom_records = invenio_records_lom.views:create_records_bp",
        ],
        "invenio_jsonschemas.schemas": [
            "invenio_records_lom = invenio_records_lom.jsonschemas",
        ],
        "invenio_search.mappings": [
            "lomrecords = invenio_records_lom.records.mappings",
        ],
        "invenio_db.models": [
            "invenio_records_lom = invenio_records_lom.records.models",
        ],
        "invenio_i18n.translations": [
            "messages = invenio_records_lom",
        ],
    },
    extras_require=extras_require,
    install_requires=install_requires,
    setup_requires=setup_requires,
    tests_require=tests_require,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
