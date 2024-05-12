# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2024 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Common utilities for schemas."""


def get_text(value: dict) -> str:
    """Get text from langstring object."""
    try:
        return value["langstring"]["#text"]
    except KeyError:
        return ""


def get_lang(value: dict) -> str:
    """Get lang from langstring object."""
    try:
        return value["langstring"]["lang"]
    except KeyError:
        return ""


def get_related(obj: dict, relation_kind: str, catalog: str = "repo-pid") -> list:
    """Get dereferenced records that are `relation_kind`-related to `obj`."""
    results = []
    for relation in obj["metadata"].get("relation", []):
        if get_text(relation["kind"]["value"]) != relation_kind:
            continue

        for identifier in relation["resource"]["identifier"]:
            if identifier["catalog"] != catalog:
                continue

            results.append(identifier)

    return results


def get_newest_part(obj: dict):  # noqa: ANN201
    """Get newest dereferenced record that is "haspart"-related to `obj`."""
    parts = get_related(obj, relation_kind="haspart")
    return parts[-1]
