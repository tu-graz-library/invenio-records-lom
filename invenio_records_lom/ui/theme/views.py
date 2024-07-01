# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.


"""invenio data model for Learning object metadata."""

from flask import Blueprint, Flask, render_template

from .config import search_app_context


def search() -> str:
    """Search help guide."""
    return render_template("invenio_records_lom/search.html")


def init_theme_views(blueprint: Blueprint, app: Flask) -> None:
    """Blueprint for the routes and resource provided by invenio-records-lom."""
    routes = app.config.get("LOM_ROUTES")

    blueprint.add_url_rule(routes["record_search"], view_func=search)

    blueprint.app_context_processor(search_app_context)
