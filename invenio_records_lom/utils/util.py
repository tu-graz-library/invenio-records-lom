# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Utilities for creation of LOM-compliant metadata."""

# allow `list[str]` annotation, PEP585 makes this unnecessary for python>=3.9
from __future__ import annotations

import copy
import json
import typing as t
from collections.abc import MutableMapping
from pathlib import Path


class DotAccessWrapper(MutableMapping):
    """Provides getting/setting for passed-in mapping via dot-notated keys.

    Getting:
    >> wrapper = DotAccessWrapper(data:={"a":{"b": [0,1,2]}})
    >> wrapper["a.b.0"]  # same as `data["a"]["b"][0]`
    >> wrapper["a.b.-1"]  # same as `data["a"]["b"][-1]`
    Note that int-castable subkeys are int-casted (to allow easy working with lists).

    When setting, non-existing submappings are created:
    >> wrapper = DotAccessWrapper(data:={})
    >> wrapper["a.b"] = 3  # same as `data["a"]["b"] = 3`, data["a"] is created as a dict
    Note that this changes the mapping passed on initialization (if any).

    When setting, you can also create a new list-entry on the fly, using `[]` as subkey:
    >> wrapper = DotAccessWrapper(data:={})
    >> wrapper["c.[]"] = 4  # same as `data["c"].append(4)`, data["c"] is created as a list

    To be unambiguous, int-castable keys may not appear in dicts within passed-in data.
    """

    def __init__(
        self, data: t.Union[dict, list, None] = None, overwritable: bool = True
    ) -> None:
        """Constructor."""
        self.data = data if (data is not None) else {}
        self.overwritable = bool(overwritable)

    def __getitem__(self, dotted_key: str) -> t.Any:
        """Get."""
        cursor = self.data
        for subkey in self.split(dotted_key):
            self.check(cursor, subkey)
            try:
                cursor = cursor[subkey]
            except (IndexError, TypeError, ValueError) as exc:
                # `wrapper.get(key, default)` defaults only on errors of type KeyError
                raise KeyError(dotted_key) from exc
        return cursor

    def __setitem__(self, dotted_key: str, value: t.Any) -> None:
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
                self.check(cursor, subkey)
                if subkey not in cursor or next_subkey is None:
                    cursor[subkey] = next_value
                cursor = cursor[subkey]

    def __delitem__(self, dotted_key: str) -> None:
        """Delete."""
        *parent_keys, last_key = self.split(dotted_key)
        parent = self[".".join(parent_keys)]
        self.check(parent, last_key)
        del parent[last_key]  # pylint: disable=unsupported-delete-operation

    def __iter__(self) -> t.Iterator:
        """Iter."""
        return iter(self.data)

    def __len__(self) -> None:
        """Len."""
        return len(self.data)

    def __repr__(self) -> str:
        """Repr."""
        return f"<{type(self).__qualname__}({self.data!r}) at {hex(id(self))}>"

    @staticmethod
    def check(container: t.Union[dict, list], key: str) -> None:
        """Check whether `key` fulfills the unambiguity condition."""
        try:
            key = int(key)
        except ValueError:
            pass

        if isinstance(container, dict) and not isinstance(key, str):
            raise ValueError("For unambiguity, dict-keys may not be int-castable.")

    @staticmethod
    def split(dotted_key: str) -> list[t.Union[str, int]]:
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
    path = Path(__file__).resolve().parent / "learning_resource_types.json"
    return json.loads(path.read_text())


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

    oefos_path = Path(__file__).resolve().parent / filename

    line_iter = iter(oefos_path.read_text().splitlines())
    __ = next(line_iter)  # discard header
    for line in line_iter:
        # line is of form `{depth-level};"{EDV-code}";"{code}";"{title}";"{short title}"`
        # e.g. `4;"603125";"603125";"Metaethik";""`
        __, edv_code, __, name, __ = line.split(";")
        oefosdict[edv_code.strip('"')] = name.strip('"')
    return oefosdict


def langstringify(text: str, lang: t.Optional[str] = "x-none") -> dict:
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


class LOMMetadata:
    """Helper-class for easy creation of LOM-metadata JSONs."""

    # learningresourcetypes according to `https://w3id.org/kim/hcrt/scheme`
    # used in LOM.educational.learningresourcetype
    # this maps (url-ending -> label-dict) where label-dict maps (lang-code -> label)
    learningresourcetype_labels = get_learningresourcetypedict()

    # oefos_dicts map (oefos_id -> oefos_name)
    # oefos_names are needed for filling in taxonpaths
    oefosdict_by_language = {
        "de": get_oefosdict("de"),
        "en": get_oefosdict("en"),
    }

    def __init__(self, record_json: t.Optional[dict] = None) -> None:
        """Init."""
        record_json = copy.deepcopy(record_json or {})
        self.record = DotAccessWrapper(record_json, overwritable=False)

    #
    # methods for manipulating LOM's `general` category
    #
    def append_identifier(self, id_: str, catalog: str) -> None:
        """Append identifier.

        :param str catalog: The name of the cataloging scheme (e.g. "ISBN")
        :param str id_: The value of the identifier within the cataloging scheme
        """
        self.record["general.identifier.[]"] = catalogify(id_, catalog=catalog)

    def set_title(self, title: str, language_code: str) -> None:
        """Set title."""
        self.record["general.title"] = langstringify(title, lang=language_code)

    def append_language(self, language_code: str) -> None:
        """Append language."""
        self.record["general.language.[]"] = language_code

    def append_description(self, description: str, language_code: str) -> None:
        """Append description."""
        self.record["general.description.[]"] = langstringify(
            description, lang=language_code
        )

    def append_keyword(self, keyword: str, language_code: str) -> None:
        """Append keyword."""
        self.record["general.keyword.[]"] = langstringify(keyword, lang=language_code)

    #
    # methods for manipulating LOM's `lifeCycle` category
    #
    def append_contribute(self, name: str, role: str) -> None:
        """Append contribute.

        :param str name: The name of the contributing person/organisation
        :param str role: One of values LOM recommends for `lifecycle.contribute.role`
        """
        role = role.title()

        # contributes are grouped by role
        # try to find dict for passed-in `role`, create it if non-existent
        corresponding_contribute = None  # to be the contribute corresponding to `role`
        for contribute in self.record.get("lifecycle.contribute", []):
            contribute_role = contribute["role"]["value"]["langstring"]["#text"]
            if contribute_role == role:
                corresponding_contribute = contribute
                break
        else:
            corresponding_contribute = {
                "role": vocabularify(role),
                "entity": [],
            }
            self.record["lifecycle.contribute.[]"] = corresponding_contribute

        # append entity
        corresponding_contribute["entity"].append(name)

    def set_datetime(self, datetime: str) -> None:
        """Set the datetime the learning object was created.

        :param str datetime: The datetime-string in isoformat
        """
        self.record["lifecycle.datetime"] = datetime

    #
    # methods for manipulating LOM's `technical` category
    #
    def append_format(self, mimetype: str) -> None:
        """Append format."""
        self.record["technical.format.[]"] = mimetype

    def set_size(self, size: t.Union[str, int]) -> None:
        """Set size.

        :param str|int size: size in bytes (octets)
        """
        self.record["technical.size"] = str(size)

    #
    # methods for manipulating LOM's `educational` category
    #
    def append_learningresourcetype(self, learningresourcetype: str) -> None:
        """Append learning resource type.

        :param str learningresourcetype: A valid sub-url for `https://w3id.org/kim/hcrt/scheme`
        """
        labels = self.learningresourcetype_labels[learningresourcetype]
        entry = [langstringify(label, lang=lang) for lang, label in labels.items()]
        self.record["educational.learningresourcetype.[]"] = {
            "source": langstringify("https://w3id.org/kim/hcrt/scheme"),
            "id": f"https://w3id.org/kim/hcrt/{learningresourcetype}",
            "entry": entry,
        }

    def append_context(self, context: str) -> None:
        """Append context.

        :param str context: One of the values LOM recommends for `educational.context`
        """
        self.record["educational.context.[]"] = vocabularify(context)

    #
    # methods for manipulating LOM's `rights` category
    #
    def set_rights_url(self, url: str) -> None:
        """Set rights url.

        :param str url: The url of the copyright license
                        (e.g. "https://creativecommons.org/licenses/by/4.0/")
        """
        self.record["rights.copyrightandotherrestrictions"] = vocabularify("yes")
        self.record["rights.url"] = url
        self.record["rights.description"] = langstringify(url, lang="x-t-cc-url")

    #
    # methods for manipulating LOM's `classification` category
    #
    def get_oefos_classification(self) -> dict:
        """Get the classification that holds OEFOS, create it if it didn't exist."""
        # oefos are part of the unique `classification` whose `purpose` is "discipline"
        # try to find that classification, otherwise create it
        for classification in self.record.get("classification", []):
            purpose = classification["purpose"]["value"]["langstring"]["#text"]
            if purpose == "discipline":
                return (oefos_classification := classification)

        # couldn't find; create oefos-classification-dict
        oefos_classification = {
            "purpose": vocabularify("discipline"),
            "taxonpath": [],
        }
        self.record["classification.[]"] = oefos_classification
        return oefos_classification

    def create_oefos_taxonpath(
        self, oefos_id: t.Union[str, int], language_code: str = "de"
    ) -> dict:
        """Create the full OEFOS taxon-path that ends in `oefos_id`.

        Whenever assigning a classification, LOM requires the full taxonomic path.
        e.g. instead of the single classification `207413 (Surveying)`,
        the whole taxonomic path to it is required too, namely the full path
          `2 (TECHNICAL SCIENCES)`,
          `207 (Environmental Engineering, Applied Geosciences)`,
          `2074 (Geodesy, Surveying)`, and
          `207413 (Surveying)`
        is what's required.
        """
        oefos_id = str(oefos_id)
        oefosdict = self.oefosdict_by_language[language_code]
        taxon_ids = [
            oefos_id[:key]
            for key in range(len(oefos_id) + 1)
            if oefos_id[:key] in oefosdict
        ]
        taxons = []
        for taxon_id in taxon_ids:
            taxon = {
                "id": f"https://w3id.org/oerbase/vocabs/oefos2012/{taxon_id}",
                "entry": langstringify(oefosdict[taxon_id], lang=None),
            }
            taxons.append(taxon)
        return {
            "source": "https://w3id.org/oerbase/vocabs/oefos2012",
            "taxon": taxons,
        }

    def append_oefos_id(
        self, oefos_id: t.Union[str, int], language_code: str = "de"
    ) -> None:
        """Append a taxonpath corresponding to `oefos_id` to the oefos-classification.

        (The oefos-classification is the unique `classification` whose `purpose` is "discipline".)
        """
        taxonpaths = self.get_oefos_classification()["taxonpath"]
        new_taxonpath = self.create_oefos_taxonpath(oefos_id, language_code)

        # if a more comprehensive taxonpath already exists, don't add this one
        for old_taxonpath in taxonpaths:
            old_taxons = old_taxonpath["taxon"]
            new_taxons = new_taxonpath["taxon"]
            if all(taxon in old_taxons for taxon in new_taxons):
                # found previously existing taxonpath which holds a superset of new taxons
                return

        # delete less comprehensive taxonpaths (if any)
        less_comprehensive_idxs = []
        for idx, old_taxonpath in enumerate(taxonpaths):
            old_taxons = old_taxonpath["taxon"]
            new_taxons = new_taxonpath["taxon"]
            if all(taxon in new_taxons for taxon in old_taxons):
                # found previously existing taxonpath which holds a subset of new taxons
                less_comprehensive_idxs.append(idx)
        for idx in sorted(less_comprehensive_idxs, reverse=True):
            del taxonpaths[idx]

        # append
        taxonpaths.append(new_taxonpath)
