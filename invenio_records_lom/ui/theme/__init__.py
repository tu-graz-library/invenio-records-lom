# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.


"""invenio data model for Learning object metadata."""

from .views import search


def init_theme_views(blueprint, app):
    """Blueprint for the routes and resource provided by invenio-records-lom."""
    routes = app.config.get("LOM_UI_THEME_ENDPOINTS")

    blueprint.add_url_rule(routes["record-search"], view_func=search)
