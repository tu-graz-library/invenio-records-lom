# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Schemas which get wrapped by serializers."""

from .datacite import LOMToDataCite44Schema
from .dublin_core import LOMToDublinCoreRecordSchema
from .oai import LOMMetadataToOAISchema
from .ui import LOMUIRecordSchema

__all__ = (
    "LOMToDublinCoreRecordSchema",
    "LOMMetadataToOAISchema",
    "LOMToDataCite44Schema",
    "LOMUIRecordSchema",
)
