# SPDX-FileCopyrightText: 2020-2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Module tests."""

from flask import Flask

from invenio_records_lom import InvenioRecordsLOM, __version__


def test_version() -> None:
    """Test version import."""
    assert __version__


def test_init() -> None:
    """Test extension initialization."""
    app = Flask("testapp")
    ext = InvenioRecordsLOM(app)
    assert "invenio-records-lom" in app.extensions

    app = Flask("testapp")
    ext = InvenioRecordsLOM()
    assert "invenio-records-lom" not in app.extensions
    ext.init_app(app)
    assert "invenio-records-lom" in app.extensions
