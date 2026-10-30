# SPDX-FileCopyrightText: 2021-2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Serializers turning records into html-template-insertable dicts."""

from .csl import LOMToCitationStringSerializer
from .datacite import LOMToDataCite44Serializer
from .dublincore import LOMToDublinCoreJSONSerializer, LOMToDublinCoreXMLSerializer
from .oai import LOMToOAIXMLSerializer
from .ui import LOMToUIJSONSerializer

__all__ = (
    "LOMToCitationStringSerializer",
    "LOMToDataCite44Serializer",
    "LOMToDublinCoreJSONSerializer",
    "LOMToDublinCoreXMLSerializer",
    "LOMToOAIXMLSerializer",
    "LOMToUIJSONSerializer",
)
