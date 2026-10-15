# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2026 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

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
