# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

from invenio_records_resources.records.systemfields import PIDRelation

from .results import RelationLOMResult


class PIDLOMRelation(PIDRelation):
    result_cls = RelationLOMResult

    def __init__(
        self,
        key="metadata.relation",
        *,
        _value_key_suffix="entry",
        source="LOMv1.0",
        value=None,
        _catalog="repo-pid",
        **kwargs,
    ):
        """source, value, catalog as in 7.Relation of LOM-standard."""
        self.source = source
        self.value = value
        self._catalog = _catalog
        super().__init__(key=key, _value_key_suffix=_value_key_suffix, **kwargs)

    def parse_value(self, value):
        raise NotImplementedError(
            f"{self.__class__.__qualname__}.parse_value is not implemented yet"
        )

    def _get_parent(self, record, keys):
        raise NotImplementedError(
            f"{self.__class__.__qualname__}._get_parent is not implemented yet"
        )

    def set_value(self, record, value):
        raise NotImplementedError(
            f"{self.__class__.__qualname__}.set_value is not implemented yet"
        )

    def clear_value(self, record):
        raise NotImplementedError(
            f"{self.__class__.__qualname__}.clear_value is not implemented yet"
        )

    def exists_many(self, ids):
        raise NotImplementedError(
            f"{self.__class__.__qualname__}.exists_many is not implemented yet"
        )
