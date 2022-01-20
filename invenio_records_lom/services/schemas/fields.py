# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Custom marshmallow fields."""

import typing as t
from collections.abc import Container

from marshmallow import fields


class ControlledVocabularyField(fields.String):
    """A controlled vocabulary field."""

    default_error_messages = {
        "not_in_vocabulary": "Value {string!r} not in controlled vocabulary {vocabulary!r}."
    }

    def __init__(self, *, vocabulary: Container = None, **kwargs):
        """Initialize self."""
        assert isinstance(vocabulary, t.Container)
        self.vocabulary = vocabulary
        super().__init__(**kwargs)

    def _deserialize(
        self,
        value: t.Any,
        attr: t.Optional[str],
        data: t.Optional[t.Dict[str, t.Any]],
        **kwargs
    ):
        string = super()._deserialize(value, attr, data, **kwargs)
        if string not in self.vocabulary:
            raise self.make_error(
                "not_in_vocabulary", vocabulary=self.vocabulary, string=string
            )
        return string
