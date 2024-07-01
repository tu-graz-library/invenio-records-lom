# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2024 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Custom marshmallow fields."""

from collections.abc import Container
from types import MappingProxyType
from typing import Any

from marshmallow import fields


class ControlledVocabularyField(fields.String):
    """A controlled vocabulary field."""

    default_error_messages = MappingProxyType(
        {
            "not_in_vocabulary": "Value {string!r} not in controlled vocabulary {vocabulary!r}.",
        },
    )

    def __init__(self, *, vocabulary: Container | None = None, **kwargs: dict) -> None:
        """Initialize self."""
        assert isinstance(vocabulary, Container)
        self.vocabulary = vocabulary
        super().__init__(**kwargs)

    def _deserialize(
        self,
        value: Any,  # noqa: ANN401
        attr: str | None,
        data: dict | None,
        **kwargs: dict,
    ) -> str:
        string = super()._deserialize(value, attr, data, **kwargs)
        if string not in self.vocabulary:
            msg = "not_in_vocabulary"
            raise self.make_error(msg, vocabulary=self.vocabulary, string=string)
        return string
