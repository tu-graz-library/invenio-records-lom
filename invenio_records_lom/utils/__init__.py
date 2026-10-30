# SPDX-FileCopyrightText: 2022-2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Utilities for creation of LOM-compliant metadata."""

from .metadata import LOMCourseMetadata, LOMMetadata, LOMRecordData
from .stats import build_record_unique_id
from .util import (
    DotAccessWrapper,
    LOMDuplicateRecordError,
    check_about_duplicate,
    create_record,
    get_learningresourcetypedict,
    get_oefosdict,
    update_record,
)
from .vcard import make_lom_vcard

__all__ = (
    "DotAccessWrapper",
    "LOMCourseMetadata",
    "LOMDuplicateRecordError",
    "LOMMetadata",
    "LOMRecordData",
    "build_record_unique_id",
    "check_about_duplicate",
    "create_record",
    "get_learningresourcetypedict",
    "get_oefosdict",
    "make_lom_vcard",
    "update_record",
)
