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

import pytest
from invenio_app.factory import create_app as invenio_create_app


@pytest.fixture(scope="module")
def create_app():
    """Application factory fixture.

    pytest-invenio uses this in creating the `base_app`-fixture.
    """
    return invenio_create_app
