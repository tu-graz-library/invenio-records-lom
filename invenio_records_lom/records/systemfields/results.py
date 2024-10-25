# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2024 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Results for relations system field."""

from invenio_records.systemfields.relations import RelationResult

from ...utils import DotAccessWrapper


class RelationLOMResult(RelationResult):
    """Relation access result."""

    def __call__(self, *, force: bool = True) -> None:
        """Resolve the relation."""
        msg = f"{self.__class__.__qualname__}.__call__ is not implemented yet"
        raise NotImplementedError(msg)

    def _lookup_id(self) -> None:
        msg = f"{self.__class__.__qualname__}._lookup_id is not implemented yet"
        raise NotImplementedError(msg)

    def validate(self) -> bool:
        """Validate the field."""
        # this gets called on service.publish()->record.commit()->extension.pre_commit()
        # TODO: raise when json is ill-formed

    def _apply_items(
        self,
        func: callable,
        keys: list[str] | None = None,
        attrs: dict | None = None,
    ) -> None:
        relations = self.record.get("metadata", {}).get("relation", [])
        queue = list(relations)  # queue for BFS, containing all visited relations
        for relation in queue:
            kind = relation.get("kind", {})
            source = kind.get("source", {}).get("langstring", {}).get("#text")
            value = kind.get("value", {}).get("langstring", {}).get("#text")
            if source != self.source or value != self.value:
                continue

            for identifier in relation.get("resource", {}).get("identifier", []):
                if identifier.get("catalog") != self._catalog:
                    continue
                wrapper_or_none = func(
                    DotAccessWrapper(identifier),
                    keys or self.keys or keys,  # first truthy, `keys` if both are falsy
                    attrs or self.attrs,
                )
                data = wrapper_or_none.data if wrapper_or_none is not None else {}
                queue.extend(data.get("metadata", {}).get("relation", []))

    def _clean_one(
        self,
        data: dict,
        keys: list[str] | None,  # noqa: ARG002
        attrs: dict | None,  # noqa: ARG002
    ) -> None:
        """Remove all but "entry" and "catalog" key."""
        for k in list(data.keys()):
            if k not in ["catalog", "entry"]:
                del data[k]

    def dereference(
        self,
        keys: list[str] | None = None,
        attrs: dict | None = None,
    ) -> None:
        """Dereference the relation field object inside the record."""
        return self._apply_items(self._dereference_one, keys, attrs)

    def clean(
        self,
        keys: list[str] | None = None,
        attrs: dict | None = None,
    ) -> None:
        """Remove any dereferenced attributes from inside the record."""
        # gets called pre_commit, clears any dereferenced values before committing
        self._apply_items(self._clean_one, keys, attrs)

    def append(self, value) -> None:  # noqa: ANN001
        """Append a relation to the list."""
        # (2021-10-18): invenio raises here too
        msg = f"{self.__class__.__qualname__}.append is not implemented yet"
        raise NotImplementedError(msg)

    def insert(self, index, value) -> None:  # noqa: ANN001
        """Insert a relation to the list."""
        # (2021-10-18): invenio raises here too
        msg = f"{self.__class__.__qualname__}.insert is not implemented yet"
        raise NotImplementedError(msg)
