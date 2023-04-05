# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""REST API configuration."""

import marshmallow
from flask_resources import JSONSerializer, ResponseHandler
from invenio_records_resources.resources import RecordResourceConfig
from invenio_records_resources.resources.files import FileResourceConfig

from .serializers import LOMUIJSONSerializer

record_serializer = {
    "application/json": ResponseHandler(JSONSerializer()),
    "application/vnd.inveniolom.v1+json": ResponseHandler(LOMUIJSONSerializer()),
}


class LOMDraftFilesResourceConfig(FileResourceConfig):
    """LOM Draft Files Resource configuration."""

    blueprint_name = "lom_draft_files"
    url_prefix = "/lom/<pid_value>/draft"


class LOMRecordFilesResourceConfig(FileResourceConfig):
    """LOM Record Files Resource configuration."""

    allow_upload = False
    blueprint_name = "lom_record_files"
    url_prefix = "/lom/<pid_value>"


class LOMRecordResourceConfig(RecordResourceConfig):
    """LOM Record Resource configuration."""

    blueprint_name = "lom_records"
    url_prefix = "/lom"

    default_accept_mimetype = "application/json"

    routes = {
        "list": "",
        "item": "/<pid_value>",
        "item-draft": "/<pid_value>/draft",
        "item-publish": "/<pid_value>/draft/actions/publish",
        "item-pids-reserve": "/<pid_value>/draft/pids/<scheme>",
    }

    request_view_args = {
        "pid_value": marshmallow.fields.Str(),
        "scheme": marshmallow.fields.Str(),
    }

    response_handlers = record_serializer
