# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Serializers turning records into html-template-insertable dicts."""

from invenio_rdm_records.resources.serializers import UIJSONSerializer

from .schemas import LOMUIObjectSchema


class LOMUIJSONSerializer(UIJSONSerializer):
    """Wrapper with some convenience functions around a marshmallow-schema."""

    object_schema_cls = LOMUIObjectSchema


__all__ = ("LOMUIJSONSerializer",)
