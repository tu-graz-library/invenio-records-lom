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
from faker import Faker
from flask_principal import Identity, UserNeed
from invenio_access.permissions import any_user, system_process
from invenio_app.factory import create_app as invenio_create_app

from invenio_records_lom.fixtures import create_fake_data


@pytest.fixture(scope="module")
def app_config(app_config):
    """Override pytest-invenio app_config-fixture."""
    # Enable DOI minting...
    app_config["DATACITE_ENABLED"] = True
    app_config["DATACITE_USERNAME"] = "INVALID"
    app_config["DATACITE_PASSWORD"] = "INVALID"
    app_config["DATACITE_PREFIX"] = "10.1234"
    # ...but fake it

    return app_config


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
def identity():
    """Identity fixture with rights to interact with service."""
    i = Identity(1)
    i.provides.add(UserNeed(1))
    i.provides.add(any_user)
    i.provides.add(system_process)
    return i


@pytest.fixture(scope="function")
def service(base_app, location):
    """Service fixture."""
    return base_app.extensions["invenio-records-lom"].records_service


@pytest.fixture(scope="module")
def full_lom_metadata(base_app):
    """Python dict/list-nesting in LOM-format, containing all valid fields."""
    fake = Faker()
    Faker.seed(42)  # for reproducibility: always generate same metadata
    with base_app.app_context():
        return create_fake_data(fake, resource_type="unit")
