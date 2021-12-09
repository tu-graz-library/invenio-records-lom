# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Module tests."""

from flask import Flask

from invenio_records_lom import InvenioRecordsLOM


def test_version():
    """Test version import."""
    from invenio_records_lom import __version__

    assert __version__


def test_init():
    """Test extension initialization."""
    app = Flask("testapp")
    ext = InvenioRecordsLOM(app)
    assert "invenio-records-lom" in app.extensions

    app = Flask("testapp")
    ext = InvenioRecordsLOM()
    assert "invenio-records-lom" not in app.extensions
    ext.init_app(app)
    assert "invenio-records-lom" in app.extensions
