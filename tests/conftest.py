# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Pytest configuration.

See https://pytest-invenio.readthedocs.io/ for documentation on which test
fixtures are available.
"""

import shutil
import tempfile

import pytest
from flask_principal import Identity
from invenio_access import any_user
from invenio_app.factory import create_app as invenio_create_app


@pytest.fixture(scope="module")
def create_app():
    """Application factory fixture.

    pytest-invenio uses this in creating the `base_app`-fixture.
    """
    return invenio_create_app


@pytest.fixture
def cli_location(db):
    """Fixture for invenio file-location.

    Adapted to work with `<Flask-obj>.test_cli_runner`.
    """
    from invenio_files_rest.models import Location

    uri = tempfile.mkdtemp()
    location_obj = Location(name="pytest-location", uri=uri, default=True)

    db.session.add(location_obj)
    db.session.commit()

    yield location_obj

    # can't use location_obj.uri here, as test_cli_runner expunges
    # database-commits on teardown
    shutil.rmtree(uri)


@pytest.fixture
def identity_any_user():
    """Simple identity fixture."""
    i = Identity(1)
    i.provides.add(any_user)
    return i


@pytest.fixture(scope="function")
def service(base_app, location):
    """Service fixture."""
    return base_app.extensions["invenio-records-lom"].records_service
