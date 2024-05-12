# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2024 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""User interface utilities."""

from flask import Blueprint, Flask

from .records import init_records_views
from .theme import init_theme_views


def create_blueprint(app: Flask) -> Blueprint:
    """Return blueprint with registered routes."""
    blueprint = Blueprint(
        "invenio_records_lom",
        __name__,
        template_folder="../templates",
        static_folder="../static",
        url_prefix="/oer",
    )

    init_records_views(blueprint, app)
    init_theme_views(blueprint, app)

    return blueprint
