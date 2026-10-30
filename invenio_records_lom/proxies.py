# SPDX-FileCopyrightText: 2020-2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Proxy definitions."""

from typing import TYPE_CHECKING, cast

from flask import current_app
from werkzeug.local import LocalProxy

if TYPE_CHECKING:
    from .ext import InvenioRecordsLOM

current_records_lom: InvenioRecordsLOM = cast(
    "InvenioRecordsLOM",
    LocalProxy(lambda: current_app.extensions["invenio-records-lom"]),
)
"""Proxy to the extension."""
