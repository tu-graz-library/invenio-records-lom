# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Utilities for creation of LOM-compliant metadata."""

from .util import (
    DotAccessWrapper,
    LOMMetadata,
    get_learningresourcetypedict,
    get_oefosdict,
)

__all__ = (
    "DotAccessWrapper",
    "get_learningresourcetypedict",
    "get_oefosdict",
    "LOMMetadata",
)
