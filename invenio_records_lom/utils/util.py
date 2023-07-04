# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2023 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Utilities for creation of LOM-compliant metadata."""


from collections.abc import MutableMapping
from csv import reader
from importlib import resources
from json import load
from typing import Any, Iterator, Optional, Union


class DotAccessWrapper(MutableMapping):
    """Provides getting/setting for passed-in mapping via dot-notated keys.

    Getting:
    >> wrapper = DotAccessWrapper(data:={"a":{"b": [0,1,2]}})
    >> wrapper["a.b.0"]  # same as `data["a"]["b"][0]`
    >> wrapper["a.b.-1"]  # same as `data["a"]["b"][-1]`
    Note that int-castable subkeys are int-casted (to allow easy working with lists).

    When setting, non-existing submappings are created:
    >> wrapper = DotAccessWrapper(data:={})

    same as `data["a"]["b"] = 3`, data["a"] is created as a dict
    >> wrapper["a.b"] = 3

    Note that this changes the mapping passed on initialization (if any).

    When setting, you can also create a new list-entry on the fly, using `[]` as subkey:
    >> wrapper = DotAccessWrapper(data:={})

    same as `data["c"].append(4)`, data["c"] is created as a list
    >> wrapper["c.[]"] = 4

    To be unambiguous, int-castable keys may not appear in dicts within passed-in data.
    """

    def __init__(
        self,
        data: Union[dict, list, None] = None,
        overwritable: bool = True,
    ) -> None:
        """Constructor."""
        self.data = data if (data is not None) else {}
        self.overwritable = overwritable

    def __getitem__(self, dotted_key: str) -> Any:
        """Get."""
        cursor = self.data
        for subkey in self.split(dotted_key):
            self.ascertain_unambiguity(cursor, subkey)
            try:
                cursor = cursor[subkey]
            except (IndexError, TypeError, ValueError) as exc:
                # `wrapper.get(key, default)` defaults only on errors of type KeyError
                raise KeyError(dotted_key) from exc
        return cursor

    def __setitem__(self, dotted_key: str, value: Any) -> None:
        """Set."""
        if not self.overwritable:
            if "[]" not in self.split(dotted_key) and dotted_key in self:
                raise KeyError(
                    f"Tried to overwrite {dotted_key!r} when overwriting is disabled."
                )

        cursor = self.data
        subkeys = self.split(dotted_key)
        for subkey, next_subkey in zip(subkeys, subkeys[1:] + [None]):
            # the next key allows to judge what the next value should be
            next_value = (
                [] if next_subkey == "[]" else value if next_subkey is None else {}
            )
            if subkey == "[]":
                cursor.append(next_value)
                cursor = cursor[-1]
            else:
                self.ascertain_unambiguity(cursor, subkey)
                if subkey not in cursor or next_subkey is None:
                    cursor[subkey] = next_value
                cursor = cursor[subkey]

    def __delitem__(self, dotted_key: str) -> None:
        """Delete."""
        *parent_keys, last_key = self.split(dotted_key)
        parent = self[".".join(str(key) for key in parent_keys)]
        self.ascertain_unambiguity(parent, last_key)
        del parent[last_key]  # pylint: disable=unsupported-delete-operation

    def __iter__(self) -> Iterator:
        """Iter."""
        return iter(self.data)

    def __len__(self) -> None:
        """Len."""
        return len(self.data)

    def __repr__(self) -> str:
        """Repr."""
        return f"<{type(self).__qualname__}({self.data!r}) at {hex(id(self))}>"

    @staticmethod
    def ascertain_unambiguity(container: Union[dict, list], key: str) -> None:
        """Check whether `key` is unambiguous within `container`."""
        try:
            int(key)  # try to int-cast key
            key_is_int_castable = True  # int-casting attempt succeeded
        except ValueError:
            key_is_int_castable = False  # int-casting attempt failed

        if key_is_int_castable and isinstance(container, dict):
            # it's not clear whether key is supposed to be int-casted or not
            # since dicts take both when using an int-castable key, you probably
            # meant to use it with a list anyway...
            raise ValueError("For unambiguity, dict-keys may not be int-castable.")

    @staticmethod
    def split(dotted_key: str) -> list[Union[str, int]]:
        """Split `dotted_key` into its subkeys."""
        res = []
        for subkey in dotted_key.split("."):
            try:
                res.append(int(subkey))
            except ValueError:
                res.append(subkey)
        return res


def get_learningresourcetypedict() -> dict[str, dict[str, str]]:
    """Get learningresourcetypes-dict.

    Maps ((url-ending for "https://w3id.org/kim/hcrt/scheme/") -> labels_by_language),
    where labels_by_language maps (language_code -> label).
    """
    with resources.open_text(__package__, "learning_resource_types.json") as file_like:
        return load(file_like)


def get_oefosdict(language_code: str = "de") -> dict[str, str]:
    """Get oefos-dict, which maps OEFOS-codes to subject-names."""
    oefosdict = {}  # to be result

    filenames_by_language = {
        "de": "OEFOS2012_DE_CTI_20211111_154218_utf8.csv",
        "en": "OEFOS2012_EN_CTI_20211111_154228_utf8.csv",
    }
    if language_code.lower() not in filenames_by_language:
        raise ValueError(f"OEFOS aren't available for language_code {language_code!r}.")
    filename = filenames_by_language[language_code.lower()]

    with resources.open_text(__package__, filename) as file_pointer:
        file_reader = reader(file_pointer, delimiter=";")

        # discard header
        next(file_reader)

        for __, edv_code, __, name, __ in file_reader:
            oefosdict[edv_code] = name

    return oefosdict


def langstringify(text: str, lang: Optional[str] = "x-none") -> dict:
    """Wraps `text` and `lang` into a langstring-dict as per LOM-standard.

    If `lang` is falsy, the output won't have a "lang"-field.
    """
    langstring = {}
    langstring["#text"] = text
    if lang:
        langstring["lang"] = lang
    return {"langstring": langstring}


def vocabularify(value: str, source: str = "LOMv1.0") -> dict:
    """Wraps `value` and `source` into a vocabulary-dict as per LOM-standard."""
    return {
        "source": langstringify(source),
        "value": langstringify(value),
    }


def catalogify(value: str, catalog: str) -> dict:
    """Wraps `value` and `catalog` into a catalog-dict as per LOM-standard."""
    return {
        "catalog": catalog,
        "entry": langstringify(value),
    }


def durationify(datetime: str, description: str):
    """Wraps `datetime` and `description` into a duration-dict as per LOM-standard.

    If either parameter is falsy, the output won't have the corresponding field.
    """
    if not datetime and not description:
        raise ValueError("At least one of `datetime`, `description` need be truthy.")

    inner = {}
    if datetime:
        inner["datetime"] = datetime
    if description:
        inner["decription"] = description

    return {"duration": inner}
