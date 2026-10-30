# SPDX-FileCopyrightText: 2024-2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

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
        )
