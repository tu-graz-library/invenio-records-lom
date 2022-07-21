# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Results for relations system field."""

import typing as t

from invenio_records.systemfields.relations import RelationResult

from ...utils import DotAccessWrapper


class RelationLOMResult(RelationResult):
    """Relation access result."""

    def __call__(self, force=True):
        """Resolve the relation."""
        raise NotImplementedError(
            f"{self.__class__.__qualname__}.__call__ is not implemented yet"
        )

    def _lookup_id(self):
        raise NotImplementedError(
            f"{self.__class__.__qualname__}._lookup_id is not implemented yet"
        )

    def validate(self):
        """Validate the field."""
        # this gets called on service.publish()->record.commit()->extension.pre_commit()
        # TODO: raise when json is ill-formed

    def _apply_items(
        self,
        func: callable,
        keys: t.Union[t.List[str], None] = None,
        attrs: dict = None,
    ):
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
        keys: t.Union[t.List[str], None],
        attrs: t.Optional[dict],
    ):
        """Remove all but "entry" and "catalog" key."""
        for k in list(data.keys()):
            if k not in ["catalog", "entry"]:
                del data[k]

    def dereference(
        self,
        keys: t.Union[t.List[str], None] = None,
        attrs: t.Optional[dict] = None,
    ):
        """Dereference the relation field object inside the record."""
        return self._apply_items(self._dereference_one, keys, attrs)

    def clean(
        self,
        keys: t.Union[t.List[str], None] = None,
        attrs: t.Optional[dict] = None,
    ):
        """Remove any dereferenced attributes from inside the record."""
        # gets called pre_commit, clears any dereferenced values before committing
        self._apply_items(self._clean_one, keys, attrs)

    def append(self, value):
        """Append a relation to the list."""
        # (2021-10-18): invenio raises here too
        raise NotImplementedError(
            f"{self.__class__.__qualname__}.append is not implemented yet"
        )

    def insert(self, index, value):
        """Insert a relation to the list."""
        # (2021-10-18): invenio raises here too
        raise NotImplementedError(
            f"{self.__class__.__qualname__}.insert is not implemented yet"
        )
