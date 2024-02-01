# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2024 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Serializers turning records into html-template-insertable dicts."""

from .datacite import LOMToDataCite44Serializer
from .dublincore import LOMToDublinCoreJSONSerializer, LOMToDublinCoreXMLSerializer
from .oai import LOMToOAIXMLSerializer
from .ui import LOMToUIJSONSerializer

__all__ = (
    "LOMToDataCite44Serializer",
    "LOMToDublinCoreJSONSerializer",
    "LOMToDublinCoreXMLSerializer",
    "LOMToOAIXMLSerializer",
    "LOMToUIJSONSerializer",
)
