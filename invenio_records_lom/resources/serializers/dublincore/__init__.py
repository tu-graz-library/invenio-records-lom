# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""DublinCore Serializer."""

from .serializer import LOMToDublinCoreJSONSerializer, LOMToDublinCoreXMLSerializer

__all__ = (
    "LOMToDublinCoreJSONSerializer",
    "LOMToDublinCoreXMLSerializer",
)
