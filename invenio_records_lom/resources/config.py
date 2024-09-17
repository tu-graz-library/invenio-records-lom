# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2024 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""REST API configuration."""

from types import MappingProxyType

from flask_resources import JSONSerializer, ResponseHandler
from invenio_rdm_records.resources import IIIFResourceConfig
from invenio_records_resources.resources import RecordResourceConfig
from invenio_records_resources.resources.files import FileResourceConfig
from marshmallow import fields

from .serializers import LOMToUIJSONSerializer

record_serializers = {
    "application/json": ResponseHandler(JSONSerializer()),
    "application/vnd.inveniolom.v1+json": ResponseHandler(LOMToUIJSONSerializer()),
}

url_prefix = "/oer"


class LOMDraftFilesResourceConfig(FileResourceConfig):
    """LOM Draft Files Resource configuration."""

    blueprint_name = "lom_draft_files"
    url_prefix = f"{url_prefix}/<pid_value>/draft"

    response_handlers = {  # noqa: RUF012
        "application/vnd.inveniolom.v1+json": FileResourceConfig.response_handlers[
            "application/json"
        ],
        **FileResourceConfig.response_handlers,
    }


class LOMRecordFilesResourceConfig(FileResourceConfig):
    """LOM Record Files Resource configuration."""

    allow_upload = False
    blueprint_name = "lom_record_files"
    url_prefix = f"{url_prefix}/<pid_value>"


class LOMRecordResourceConfig(RecordResourceConfig):
    """LOM Record Resource configuration."""

    blueprint_name = "lom_records"
    url_prefix = url_prefix

    default_accept_mimetype = "application/json"

    routes = MappingProxyType(
        {
            "list": "",
            "item": "/<pid_value>",
            "item-draft": "/<pid_value>/draft",
            "item-publish": "/<pid_value>/draft/actions/publish",
            "item-pids-reserve": "/<pid_value>/draft/pids/<scheme>",
            "user-prefix": "/user",
        },
    )

    # `flask_resources.parser.RequestParser.__init__` requires
    # `isinstance(request_view_args, dict)` to treat this correctly
    # this still *should* probably be read-only, but that would require upstream-changes
    request_view_args = {  # noqa: RUF012
        "pid_value": fields.Str(),
        "scheme": fields.Str(),
    }

    response_handlers = record_serializers


class LOMIIIFResourceConfig(IIIFResourceConfig):
    """LOM IIIF Resource Config."""

    blueprint_name = "lom_iiif"
    url_prefix = f"{url_prefix}/iiif"
