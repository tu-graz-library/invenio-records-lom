# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.


"""Configuration helper for React-SearchKit."""

from functools import partial

from flask import current_app
from invenio_search_ui.searchconfig import search_app_config


def search_app_context() -> dict:
    """Search app context processor."""
    return {
        "search_app_lom_config": partial(
            search_app_config,
            "LOM_SEARCH",
            current_app.config["LOM_FACETS"],
            current_app.config["LOM_SORT_OPTIONS"],
            "/api/oer",
            {"Accept": "application/vnd.inveniolom.v1+json"},
            app_id="InvenioRecordsLom.Search",  # unique id to distinguish amongst search-apps
        ),
        "search_app_lom_user_uploads_config": partial(
            search_app_config,
            "LOM_SEARCH_DRAFTS",
            current_app.config["LOM_FACETS"],
            current_app.config["LOM_SORT_OPTIONS"],
            "/api/user/oer",
            {"Accept": "application/vnd.inveniolom.v1+json"},
            app_id="InvenioRecordsLom.Search",  # unique id to distinguish amongst search-apps
        ),
    }
