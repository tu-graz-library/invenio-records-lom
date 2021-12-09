# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Relations system field."""

from invenio_records_resources.records.systemfields import PIDRelation

from .results import RelationLOMResult


class PIDLOMRelation(PIDRelation):
    """PIDRelation with recursive dereferencing."""

    result_cls = RelationLOMResult

    def __init__(
        self,
        key: str = "metadata.relation",
        *,
        _value_key_suffix: str = "entry",  # overwrite parent-class default
        source: str = "LOMv1.0",  # matches against {self.key}.kind.source
        value: str = None,  # matches against {self.key}.kind.value
        _catalog: str = "repo-pid",  # matches against {self.key}.resource.identifier.catalog
        **kwargs,
    ):
        """`source`, `value`, `catalog` as in `7.Relation` of LOM-standard."""
        self.source = source
        self.value = value
        self._catalog = _catalog
        super().__init__(key=key, _value_key_suffix=_value_key_suffix, **kwargs)

    def parse_value(self, value):
        """Parse a record (or ID) to the ID to be stored."""
        raise NotImplementedError(
            f"{self.__class__.__qualname__}.parse_value is not implemented yet"
        )

    def set_value(self, record, value):
        """Set the relation value."""
        raise NotImplementedError(
            f"{self.__class__.__qualname__}.set_value is not implemented yet"
        )

    def clear_value(self, record):
        """Clear the relation value."""
        raise NotImplementedError(
            f"{self.__class__.__qualname__}.clear_value is not implemented yet"
        )

    def exists_many(self, ids):
        """Default multiple existence check by a list of IDs."""
        raise NotImplementedError(
            f"{self.__class__.__qualname__}.exists_many is not implemented yet"
        )
