# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""CSL serializers."""

from collections.abc import Callable

from citeproc_styles import get_style_filepath
from flask_resources import BaseListSchema, JSONSerializer, MarshmallowSerializer
from invenio_rdm_records.resources.serializers.csl import get_citation_string

from .schema import LOMToCSLSchema

type StyleLocaleTuple = tuple[str | None, str | None]


# Copied from `invenio-rdm-records`'s `StringCitationSerializer`, with some changes:
class LOMToCitationStringSerializer(MarshmallowSerializer):
    """Marshmallow-based citation-string serializer for LOM records."""

    # defaults for when url-args aren't provided
    default_style = "harvard1"
    default_locale = "en-US"

    def __init__(
        self,
        url_args_retriever: StyleLocaleTuple | Callable[[], StyleLocaleTuple],
        **serializer_options,  # noqa: ANN003
    ) -> None:
        """Construct."""
        super().__init__(
            format_serializer_cls=JSONSerializer,
            object_schema_cls=LOMToCSLSchema,
            list_schema_cls=BaseListSchema,
            **serializer_options,
        )
        self.url_args_retriever = url_args_retriever

    def serialize_object(self, record: dict) -> str:
        """Serialize a single record."""
        style, locale = (
            self.url_args_retriever()
            if callable(self.url_args_retriever)
            else self.url_args_retriever
        )

        style = style or self.default_style
        locale = locale or self.default_locale
        style_filepath = get_style_filepath(style.lower())

        return get_citation_string(
            self.dump_obj(record),
            record["id"],
            style_filepath,
            locale,
        )
