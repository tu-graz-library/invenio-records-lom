# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""REST API configuration."""

from flask_resources import ResponseHandler
from invenio_records_resources.resources import RecordResourceConfig

from .serializers import LOMUIJSONSerializer

record_serializer = {
    "application/vnd.invenio.lom.v1+json": ResponseHandler(LOMUIJSONSerializer()),
}


class LOMRecordResourceConfig(RecordResourceConfig):
    """LOM Record Resource configuration."""

    blueprint_name = "lom_records"
    url_prefix = "/lom"

    default_accept_mimetype = "application/json"

    routes = {
        "list": "",
        "item": "/<pid_value>",
    }

    response_handlers = record_serializer
