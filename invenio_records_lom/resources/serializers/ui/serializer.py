# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""UI serializer."""


from flask_resources import BaseListSchema, JSONSerializer, MarshmallowSerializer

from .schema import LOMUIRecordSchema


class LOMToUIJSONSerializer(MarshmallowSerializer):
    """Wrapper with some convenience functions around a marshmallow-schema."""

    def __init__(self) -> None:
        """Initialize serializer with arguments for LOM-serialization."""
        super().__init__(
            format_serializer_cls=JSONSerializer,
            object_schema_cls=LOMUIRecordSchema,
            list_schema_cls=BaseListSchema,
            schema_context={"object_key": "ui"},
        )
