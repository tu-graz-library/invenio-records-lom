# SPDX-FileCopyrightText: 2021-2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Blueprints from resources, for REST-API routes."""

from flask import Blueprint, Flask

blueprint = Blueprint("invenio_records_lom_ext", __name__)


def create_records_bp(app: Flask) -> Blueprint:
    """Create records blueprint."""
    ext = app.extensions["invenio-records-lom"]
    return ext.records_resource.as_blueprint()


def create_draft_files_bp(app: Flask) -> Blueprint:
    """Create draft files blueprint."""
    ext = app.extensions["invenio-records-lom"]
    return ext.draft_files_resource.as_blueprint()


def create_record_files_bp(app: Flask) -> Blueprint:
    """Create record files bluprint."""
    ext = app.extensions["invenio-records-lom"]
    return ext.record_files_resource.as_blueprint()


def create_iiif_bp(app: Flask) -> Blueprint:
    """Create IIIF blueprint."""
    ext = app.extensions["invenio-records-lom"]
    return ext.iiif_resource.as_blueprint()
