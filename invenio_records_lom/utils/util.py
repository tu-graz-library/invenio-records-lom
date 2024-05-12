# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Utilities for creation of LOM-compliant metadata."""

from collections.abc import MutableMapping
from csv import reader
from importlib import resources
from json import load
from pathlib import Path
from re import compile as re_compile
from re import sub
from time import sleep
from typing import Iterator

from flask_principal import Identity
from invenio_records_resources.services.base import Service
from invenio_records_resources.services.records.results import RecordItem
from invenio_search import RecordsSearch
from invenio_search.engine import dsl
from marshmallow.exceptions import ValidationError


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
        data: dict | list | None = None,
        *,
        overwritable: bool = True,
    ) -> None:
        """Construct."""
        self.data = data if (data is not None) else {}
        self.overwritable = overwritable

    def __getitem__[T](self, dotted_key: str) -> T:
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

    def __setitem__[T](self, dotted_key: str, value: T) -> None:
        """Set."""
        if (
            not self.overwritable
            and "[]" not in self.split(dotted_key)
            and dotted_key in self
        ):
            msg = f"Tried to overwrite {dotted_key!r} when overwriting is disabled."
            raise KeyError(msg)

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
        del parent[last_key]

    def __iter__(self) -> Iterator:
        """Iterate."""
        return iter(self.data)

    def __len__(self) -> None:
        """Len."""
        return len(self.data)

    def __repr__(self) -> str:
        """Repr."""
        return f"<{type(self).__qualname__}({self.data!r}) at {hex(id(self))}>"

    @staticmethod
    def ascertain_unambiguity(container: dict | list, key: str) -> None:
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
            msg = "For unambiguity, dict-keys may not be int-castable."
            raise ValueError(msg)

    @staticmethod
    def split(dotted_key: str) -> list[str | int]:
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
    traversable = resources.files(__package__).joinpath("learning_resource_types.json")
    with traversable.open("r", encoding="utf-8") as file_like:
        return load(file_like)


def get_oefosdict(language_code: str = "de") -> dict[str, str]:
    """Get oefos-dict, which maps OEFOS-codes to subject-names."""
    filenames_by_language = {
        "de": "OEFOS2012_DE_CTI_20211111_154218_utf8.csv",
        "en": "OEFOS2012_EN_CTI_20211111_154228_utf8.csv",
    }

    if language_code.lower() not in filenames_by_language:
        msg = f"OEFOS aren't available for language_code {language_code!r}."
        raise ValueError(msg)

    filename = filenames_by_language[language_code.lower()]
    traversable = resources.files(__package__).joinpath(filename)
    with traversable.open("r", encoding="utf-8") as file_pointer:
        file_reader = reader(file_pointer, delimiter=";")

        # discard header
        next(file_reader)

        return {edv_code: name for __, edv_code, __, name, __ in file_reader}


def langstringify(text: str, lang: str | None = "x-none") -> dict:
    """Wrap `text` and `lang` into a langstring-dict as per LOM-standard.

    If `lang` is falsy, the output won't have a "lang"-field.
    """
    langstring = {}
    langstring["#text"] = text
    if lang:
        langstring["lang"] = lang
    return {"langstring": langstring}


def vocabularify(value: str, source: str = "LOMv1.0") -> dict:
    """Wrap `value` and `source` into a vocabulary-dict as per LOM-standard."""
    return {
        "source": langstringify(source),
        "value": langstringify(value),
    }


def catalogify(value: str, catalog: str) -> dict:
    """Wrap `value` and `catalog` into a catalog-dict as per LOM-standard."""
    return {
        "catalog": catalog,
        "entry": langstringify(value),
    }


def durationify(datetime: str, description: str) -> dict:
    """Wrap `datetime` and `description` into a duration-dict as per LOM-standard.

    If either parameter is falsy, the output won't have the corresponding field.
    """
    if not datetime and not description:
        msg = "At least one of `datetime`, `description` need be truthy."
        raise ValueError(msg)

    inner = {}
    if datetime:
        inner["datetime"] = datetime
    if description:
        inner["decription"] = description

    return {"duration": inner}


def standardize_url(url: str) -> str:
    """Return standardized version of `url`.

    If `url`'s scheme is "http" or "https", make it "https".
    Also ensure existence of a trailing "/".
    """
    pattern = re_compile("^https?://(.*?)/?$")
    if m := pattern.match(url):
        middle = m.group(1)  # excludes initial "https://", excludes trailing "/"
        return f"https://{middle}/"
    return url


class LOMDuplicateRecordError(Exception):
    """Duplicate Record Exception."""

    def __init__(self, value: str, catalog: str, id_: str) -> None:
        """Construct for class DuplicateRecordException."""
        msg = f"LOMDuplicateRecordError value: {value} with catalog: {catalog} already exists id={id_} in the database"
        super().__init__(msg)


def check_about_duplicate(identifier: str, catalog: str) -> None:
    """Check if the record with the identifier is already within the database."""
    search = RecordsSearch(index="lomrecords")

    search.query = dsl.Q(
        "bool",
        must=[
            dsl.Q(
                "match",
                **{"metadata.general.identifier.catalog.keyword": catalog},
            ),
            dsl.Q(
                "match_phrase",
                **{"metadata.general.identifier.entry.langstring.#text": identifier},
            ),
        ],
    )

    results = search.execute()

    if len(results) > 0:
        raise LOMDuplicateRecordError(
            value=identifier,
            catalog=catalog,
            id_=results[0]["id"],
        )


def add_file_to_record(
    lomid: str,
    file_path: str,
    file_service: Service,
    identity: Identity,
) -> None:
    """Add the file to the record."""
    file_ = Path(file_path)
    filename = sub(r"-([^-]*?)\.", r".", file_.name)
    data = [{"key": filename}]

    with file_.open(mode="rb") as file_pointer:
        file_service.init_files(id_=lomid, identity=identity, data=data)
        file_service.set_file_content(
            id_=lomid,
            file_key=filename,
            identity=identity,
            stream=file_pointer,
        )
        file_service.commit_file(id_=lomid, file_key=filename, identity=identity)


def create_record(
    service: Service,  # services.LOMRecordService
    data: dict,
    file_paths: list[str],
    identity: Identity,
    *,
    do_publish: bool = True,
) -> RecordItem:
    """Create record."""
    data["files"] = {"enabled": len(file_paths) > 0}
    data["access"] = {
        "access": {
            "record": "public",
            "files": "public",
        },
    }

    draft = service.create(data=data, identity=identity)

    try:
        for file_path in file_paths:
            add_file_to_record(
                lomid=draft.id,
                file_path=file_path,
                file_service=service.draft_files,
                identity=identity,
            )

        if do_publish:
            # to prevent the race condition bug.
            # see https://github.com/inveniosoftware/invenio-rdm-records/issues/809
            sleep(0.5)

            return service.publish(id_=draft.id, identity=identity)
    except (FileNotFoundError, ValidationError):
        service.delete_draft(id_=draft.id, identity=identity)
        raise

    return draft


def update_record(
    pid: str,
    service: Service,  # services.LOMRecordService
    data: dict,
    identity: Identity,
    *,
    do_publish: bool = True,
) -> None:
    """Update record."""
    service.update_draft(id_=pid, data=data, identity=identity)

    if do_publish:
        service.publish(id_=pid, identity=identity)
