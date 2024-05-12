# -*- coding: utf-8 -*-
#
# Copyright (C) 2019-2021 CERN.
# Copyright (C) 2019-2021 Northwestern University.
# Copyright (C)      2021 TU Wien.
# Copyright (C) 2021-2024 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
# For the original code see the NOTE below.


# NOTE:
# copy-pasted code from invenio_app_rdm/records_ui/views/records.py
# copy-pasted as to avoid invenio_app_rdm as a dependency

"""Errors to be registered in flask."""

from flask import current_app, render_template
from flask_login import current_user


def not_found_error(error: Exception) -> tuple[str, int]:  # noqa: ARG001
    """Handle for 'Not Found' errors."""
    return render_template(current_app.config["THEME_404_TEMPLATE"]), 404


def record_tombstone_error(error: Exception) -> tuple[str, int]:  # noqa: ARG001
    """Tombstone page."""
    return render_template("invenio_app_rdm/records/tombstone.html"), 410


def record_permission_denied_error(error: Exception) -> tuple[str, int]:  # noqa: ARG001
    """Handle permission denier error on record views."""
    if not current_user.is_authenticated:
        # trigger the flask-login unauthorized handler
        return current_app.login_manager.unauthorized()
    return render_template(current_app.config["THEME_403_TEMPLATE"]), 403
