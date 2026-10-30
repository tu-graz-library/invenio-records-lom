# SPDX-FileCopyrightText: 2024-2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""DublinCore serializer."""

from dcxml import simpledc
from flask_resources import BaseListSchema, MarshmallowSerializer
from flask_resources.serializers import JSONSerializer, SimpleSerializer

from .schema import LOMToDublinCoreRecordSchema


class LOMToDublinCoreJSONSerializer(MarshmallowSerializer):
    """Marshmallow based Dublin Core serializer for records."""

    def __init__(self, **kwargs: dict) -> None:
        """Construct."""
        super().__init__(
            format_serializer_cls=JSONSerializer,
            object_schema_cls=LOMToDublinCoreRecordSchema,
            list_schema_cls=BaseListSchema,
            **kwargs,
        )


class LOMToDublinCoreXMLSerializer(MarshmallowSerializer):
    """Marshmallow based Dublin Core serializer for records.

    Note: This serializer is not suitable for serializing large number of
    records.
    """

    def __init__(self, **kwargs: dict) -> None:
        """Construct."""
        super().__init__(
            format_serializer_cls=SimpleSerializer,
            object_schema_cls=LOMToDublinCoreRecordSchema,
            list_schema_cls=BaseListSchema,
            encoder=simpledc.tostring,
            **kwargs,
        )
