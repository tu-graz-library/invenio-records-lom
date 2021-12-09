# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio-Records-LOM module for creating REST APIs."""

from .config import LOMRecordResourceConfig
from .resources import LOMRecordResource

__all__ = (
    "LOMRecordResource",
    "LOMRecordResourceConfig",
)
