# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Blueprints from resources, for REST-API routes."""

from flask import Blueprint, Flask
from flask.blueprints import BlueprintSetupState

blueprint = Blueprint("invenio_records_lom_ext", __name__)


@blueprint.record_once
def init(state: BlueprintSetupState):
    """Registers services."""
    app = state.app
    # Register services - cannot be done in extension because
    # Invenio-Records-Resources might not have been initialized.
    registry = app.extensions["invenio-records-resources"].registry
    ext = app.extensions["invenio-records-lom"]

    registry.register(ext.records_service, service_id="lom-records")
    registry.register(ext.records_service.files, service_id="lom-files")
    registry.register(ext.records_service.draft_files, service_id="lom-draft-files")


def create_records_bp(app: Flask):
    """Create records blueprint."""
    ext = app.extensions["invenio-records-lom"]
    return ext.records_resource.as_blueprint()
