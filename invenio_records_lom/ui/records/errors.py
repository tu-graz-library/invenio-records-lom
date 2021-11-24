# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Errors to be registered in flask."""

from flask import current_app, render_template
from flask_login import current_user


def not_found_error(error: Exception):
    """Handler for 'Not Found' errors."""
    return render_template(current_app.config["THEME_404_TEMPLATE"]), 404


def record_tombstone_error(error: Exception):
    """Tombstone page."""
    return render_template("invenio_app_rdm/records/tombstone.html"), 410


def record_permission_denied_error(error: Exception):
    """Handle permission denier error on record views."""
    if not current_user.is_authenticated:
        # trigger the flask-login unauthorized handler
        return current_app.login_manager.unauthorized()
    return render_template(current_app.config["THEME_403_TEMPLATE"]), 403
