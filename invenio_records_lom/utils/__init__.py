# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Utilities for creation of LOM-compliant metadata."""

from .metadata import LOMCourseMetadata, LOMMetadata
from .util import DotAccessWrapper, get_learningresourcetypedict, get_oefosdict
from .vcard import make_lom_vcard

__all__ = (
    "DotAccessWrapper",
    "get_learningresourcetypedict",
    "get_oefosdict",
    "LOMMetadata",
    "LOMCourseMetadata",
    "make_lom_vcard",
)
