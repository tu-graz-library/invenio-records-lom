# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Results for relations system field."""

import typing as t

from invenio_records.systemfields.relations import RelationResult


class RelationLOMResult(RelationResult):
    """Relation access result."""

    def __call__(self, force=True):
        """Resolve the relation."""
        raise NotImplementedError(
            f"{self.__class__.__qualname__}.__call__ is not implemented yet"
        )

    def _lookup_id(self, data):
        raise NotImplementedError(
            f"{self.__class__.__qualname__}._lookup_id is not implemented yet"
        )

    def validate(self):
        """Validate the field."""
        # this gets called on service.publish()->record.commit()->extension.pre_commit()
        # TODO: raise when json is ill-formed
        pass

    def _apply_items(self, func: callable, attrs: dict = None):
        relations = self.record.get("metadata", {}).get("relation", [])
        queue = list(relations)
        for relation in queue:
            kind = relation.get("kind", {})
            if kind.get("source") != self.source or kind.get("value") != self.value:
                continue

            for identifier in relation.get("resource", {}).get("identifier", []):
                if identifier.get("catalog") != self._catalog:
                    continue
                data = func(identifier, attrs) or {}
                queue.extend(data.get("metadata", {}).get("relation", []))

    def _clean_one(self, data: dict, attrs: t.Optional[dict]):
        """Remove all but "entry" and "catalog" key."""
        for k in list(data.keys()):
            if k not in ["catalog", "entry"]:
                del data[k]

    def dereference(self, attrs: t.Optional[dict] = None):
        """Dereference the relation field object inside the record."""
        return self._apply_items(self._dereference_one, attrs)

    def clean(self, attrs: t.Optional[dict] = None):
        """Remove any dereferenced attributes from inside the record."""
        # gets called pre_commit, clears any dereferenced values before committing
        self._apply_items(self._clean_one, attrs)

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
