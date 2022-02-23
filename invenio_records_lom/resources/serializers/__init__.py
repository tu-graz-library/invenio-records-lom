# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Serializers turning records into html-template-insertable dicts."""

from flask_resources.serializers import MarshmallowJSONSerializer
from invenio_rdm_records.resources.serializers import UIJSONSerializer

from .schemas import LOMToDataCite44Schema, LOMUIObjectSchema


class LOMUIJSONSerializer(UIJSONSerializer):
    """Wrapper with some convenience functions around a marshmallow-schema."""

    object_schema_cls = LOMUIObjectSchema


class LOMToDataCite44Serializer(MarshmallowJSONSerializer):
    """Marshmallow-based DataCite-serializer for LOM records."""

    def __init__(self, **kwargs):
        """Constructor."""
        super().__init__(schema_cls=LOMToDataCite44Schema, **kwargs)


__all__ = (
    "LOMToDataCite44Serializer",
    "LOMUIJSONSerializer",
)
