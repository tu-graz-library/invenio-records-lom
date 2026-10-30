# SPDX-FileCopyrightText: 2021-2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

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
