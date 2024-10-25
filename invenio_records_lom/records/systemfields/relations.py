# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2024 Graz University of Technology.
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
        # overwrite parent-class default
        _value_key_suffix: str = "entry.langstring.#text",
        # matches against {self.key}.kind.source.langstring.#text
        source: str = "LOMv1.0",
        # matches against {self.key}.kind.value.langstring.#text
        value: str | None = None,
        # matches against {self.key}.resource.identifier.catalog
        _catalog: str = "repo-pid",
        **kwargs: dict,
    ) -> None:
        """`source`, `value`, `catalog` as in `7.Relation` of LOM-standard."""
        self.source = source
        self.value = value
        self._catalog = _catalog
        super().__init__(key=key, _value_key_suffix=_value_key_suffix, **kwargs)

    def parse_value(self, value) -> None:  # noqa: ANN001
        """Parse a record (or ID) to the ID to be stored."""
        msg = f"{self.__class__.__qualname__}.parse_value is not implemented yet"
        raise NotImplementedError(msg)

    def set_value(self, record, value) -> None:  # noqa: ANN001
        """Set the relation value."""
        msg = f"{self.__class__.__qualname__}.set_value is not implemented yet"
        raise NotImplementedError(msg)

    def clear_value(self, record) -> bool:  # noqa: ANN001
        """Clear the relation value."""
        msg = f"{self.__class__.__qualname__}.clear_value is not implemented yet"
        raise NotImplementedError(msg)

    def exists_many(self, ids: list) -> bool:
        """Check multiple existence by a list of IDs."""
        msg = f"{self.__class__.__qualname__}.exists_many is not implemented yet"
        raise NotImplementedError(msg)
