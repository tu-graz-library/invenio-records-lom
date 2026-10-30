# SPDX-FileCopyrightText: 2021-2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Invenio-Records-LOM module for creating REST APIs."""

from .config import (
    LOMDraftFilesResourceConfig,
    LOMIIIFResourceConfig,
    LOMRecordFilesResourceConfig,
    LOMRecordResourceConfig,
)
from .resources import LOMRecordResource

__all__ = (
    "LOMDraftFilesResourceConfig",
    "LOMIIIFResourceConfig",
    "LOMRecordFilesResourceConfig",
    "LOMRecordResource",
    "LOMRecordResourceConfig",
)
