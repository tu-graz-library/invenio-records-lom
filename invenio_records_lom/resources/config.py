# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""REST API configuration."""

from invenio_records_resources.resources import RecordResourceConfig


class LOMRecordResourceConfig(RecordResourceConfig):
    """LOM Record Resource configuration."""

    blueprint_name = "lom_records"
    url_prefix = "/lom"

    routes = {
        "item": "/<pid_value>",
    }
    # TODO: fill in the rest of config
    # request_read_args =
    # request_view_args =
    # request_search_args =
    # request_headers =
    # request_body_parsers =
    # response_handlers =
    # error_handlers =
