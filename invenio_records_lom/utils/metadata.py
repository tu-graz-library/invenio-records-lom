# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2023 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""LOMMetadata class for creation of LOM-compliant metadata."""
from copy import deepcopy
from typing import Any, Optional, Union

from .util import (
    DotAccessWrapper,
    catalogify,
    get_learningresourcetypedict,
    get_oefosdict,
    langstringify,
    vocabularify,
)


class BaseLOMMetadata:
    """Base LOM Metadata."""

    def __init__(
        self,
        record_json: Optional[dict] = None,
        overwritable: bool = False,
    ) -> None:
        """Construct LOMMetadata."""
        record_json = deepcopy(record_json or {})
        self.record = DotAccessWrapper(record_json, overwritable=overwritable)

    @property
    def json(self):
        """Pipe-through for convenient access of underlying json."""
        return self.record.data

    def deduped_append(self, parent_key: str, value: Any):
        """Append `value` to `self.record[key]` if not already appended."""
        self.record.setdefault(parent_key, [])
        parent = self.record[parent_key]
        if value not in parent:
            parent.append(value)

    def append_contribute(self, name: str, role: str, path: str = None) -> None:
        """Append contribute.

        :param str name: The name of the contributing person/organisation
        :param str role: One of values LOM recommends for `lifecycle.contribute.role`
        """
        role = role.title()

        # contributes are grouped by role
        # try to find dict for passed-in `role`, create it if non-existent
        corresponding_contribute = None  # to be the contribute corresponding to `role`
        for contribute in self.record.get(path, []):
            contribute_role = contribute["role"]["value"]["langstring"]["#text"]
            if contribute_role == role:
                corresponding_contribute = contribute
                break
        else:
            corresponding_contribute = {
                "role": vocabularify(role),
                "entity": [],
            }
            self.record[f"{path}.[]"] = corresponding_contribute

        # append entity
        entities = corresponding_contribute["entity"]
        if name not in entities:
            entities.append(name)


class LOMCourseMetadata(BaseLOMMetadata):
    """Lom course Metadata."""

    def set_title(self, title: str, language_code: str) -> None:
        """Set course title."""
        self.record["course.title"] = langstringify(title, lang=language_code)

    def append_identifier(self, id_: str, catalog: str) -> None:
        """Append course identifier."""
        self.deduped_append(
            "course.identifier",
            catalogify(id_, catalog=catalog),
        )

    def append_keyword(self, keyword: str, language_code: str) -> None:
        """Append keyword."""
        self.deduped_append(
            "course.keyword",
            langstringify(keyword, lang=language_code),
        )

    def append_context(self, context: str) -> None:
        """Append context.

        :param str context: One of the values LOM recommends for `educational.context`
        """
        self.deduped_append("course.context", vocabularify(context))

    def append_language(self, language_code: str) -> None:
        """Append language."""
        self.deduped_append("course.language", language_code)

    def set_version(self, version: str, datetime: str):
        """Set version.

        :param str version: The version of this metadata
        :param str datetime: The datetime-string of this version's release in isoformat
        """
        version_dict = langstringify(version)
        version_dict["datetime"] = datetime
        self.record["course.version"] = version_dict

    def append_description(
        self,
        description: str,
        language_code: str,
    ) -> None:
        """Append educational description."""
        self.deduped_append(
            "course.description",
            langstringify(description, lang=language_code),
        )

    def append_contribute(self, name: str, role: str, path: str = None) -> None:
        """Append contribute."""
        super().append_contribute(name, role, path=path or "course.contribute")


class LOMMetadata(BaseLOMMetadata):  # pylint: disable=too-many-public-methods
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

    @classmethod
    def create(
        cls,
        resource_type: str,
        metadata: Optional[dict] = None,
        access: str = "public",
        pids: Optional[dict] = None,
        overwritable=False,
    ):
        """Create `cls` with a json that is compatible with invenio-databases.

        :param str resource_type: One of `current_app.config["LOM_RESOURCE_TYPES"]`
        :param dict metadata: The metadata to be wrapped
        :param str access: One of "public", "restricted"
        :param dict pids: For adding external pids
        """
        files_enabled = resource_type in ["file", "upload"]
        access_dict = {
            "embargo": {},
            "files": access,
            "record": access,
        }
        record_json = {
            "access": access_dict,
            "files": {"enabled": files_enabled},
            "metadata": metadata or {},
            "pids": pids or {},
            "resource_type": resource_type,
        }
        return cls(record_json, overwritable=overwritable)

    ###############
    #
    # methods for manipulating LOM's `course` category
    #
    ###############

    def append_course(self, course: LOMCourseMetadata) -> None:
        """Append course."""
        # pylint: disable-next=unsupported-membership-test
        if "courses" not in self.record["metadata"]:
            self.record["metadata.courses"] = []

        courses = self.record["metadata.courses"]

        # pylint: disable-next=not-an-iterable
        versions = [course["course"]["version"] for course in courses]

        if course.record["course.version"] not in versions:
            self.record["metadata.courses"].append(course.record.data)

    ###############
    #
    # methods for manipulating LOM's `general` category
    #
    ###############

    def append_identifier(self, id_: str, catalog: str) -> None:
        """Append identifier.

        :param str catalog: The name of the cataloging scheme (e.g. "ISBN")
        :param str id_: The value of the identifier within the cataloging scheme
        """
        self.deduped_append(
            "metadata.general.identifier",
            catalogify(id_, catalog=catalog),
        )

    def set_title(self, title: str, language_code: str) -> None:
        """Set title."""
        self.record["metadata.general.title"] = langstringify(title, lang=language_code)

    def append_language(self, language_code: str) -> None:
        """Append language."""
        self.deduped_append("metadata.general.language", language_code)

    def append_description(self, description: str, language_code: str) -> None:
        """Append description."""
        self.deduped_append(
            "metadata.general.description",
            langstringify(description, lang=language_code),
        )

    def append_keyword(self, keyword: str, language_code: str) -> None:
        """Append keyword."""
        self.deduped_append(
            "metadata.general.keyword",
            langstringify(keyword, lang=language_code),
        )

    ###############
    #
    # methods for manipulating LOM's `lifeCycle` category
    #
    ###############

    def set_version(self, version: str, datetime: str):
        """Set version.

        :param str version: The version of this metadata
        :param str datetime: The datetime-string of this version's release in isoformat
        """
        version_dict = langstringify(version)
        version_dict["datetime"] = datetime
        self.record["metadata.lifecycle.version"] = version_dict

    def append_contribute(self, name: str, role: str, path: str = None) -> None:
        """Append contribute.

        :param str name: The name of the contributing person/organisation
        :param str role: One of values LOM recommends for `lifecycle.contribute.role`
        """
        super().append_contribute(
            name, role, path=path or "metadata.lifecycle.contribute"
        )

    def set_datetime(self, datetime: str) -> None:
        """Set the datetime the learning object was created.

        :param str datetime: The datetime-string in isoformat
        """
        self.record["metadata.lifecycle.datetime"] = datetime

    ###############
    #
    # methods for manipulating LOM's `technical` category
    #
    ###############

    def append_format(self, mimetype: str) -> None:
        """Append format."""
        self.deduped_append("metadata.technical.format", mimetype)

    def set_size(self, size: Union[str, int]) -> None:
        """Set size.

        :param str|int size: size in bytes (octets)
        """
        self.record["metadata.technical.size"] = str(size)

    ###############
    #
    # methods for manipulating LOM's `educational` category
    #
    ###############

    def append_learningresourcetype(self, learningresourcetype: str) -> None:
        """Append learning resource type.

        :param str learningresourcetype: A valid sub-url for `https://w3id.org/kim/hcrt/scheme`
        """
        labels = self.learningresourcetype_labels[learningresourcetype]
        entry = [langstringify(label, lang=lang) for lang, label in labels.items()]
        learningresourcetype_dict = {
            "source": langstringify("https://w3id.org/kim/hcrt/scheme"),
            "id": f"https://w3id.org/kim/hcrt/{learningresourcetype}",
            "entry": entry,
        }
        self.deduped_append(
            "metadata.educational.learningresourcetype",
            learningresourcetype_dict,
        )

    def append_context(self, context: str) -> None:
        """Append context.

        :param str context: One of the values LOM recommends for `educational.context`
        """
        self.deduped_append("metadata.educational.context", vocabularify(context))

    def append_educational_description(
        self,
        description: str,
        language_code: str,
    ) -> None:
        """Append educational description."""
        self.deduped_append(
            "metadata.educational.description",
            langstringify(description, lang=language_code),
        )

    ###############
    #
    # methods for manipulating LOM's `rights` category
    #
    ###############

    def set_rights_url(self, url: str) -> None:
        """Set rights url.

        :param str url: The url of the copyright license
                        (e.g. "https://creativecommons.org/licenses/by/4.0/")
        """
        self.record["metadata.rights.copyrightandotherrestrictions"] = vocabularify(
            "yes"
        )
        self.record["metadata.rights.url"] = url
        self.record["metadata.rights.description"] = langstringify(
            url,
            lang="x-t-cc-url",
        )

    ###############
    #
    # methods for manipulating LOM's `relation` category
    #
    ###############

    def append_relation(self, pid: str, kind: str):
        """Append relation of kind `kind` with entry `pid`.

        `kind` is a kind, as in LOMv1.0's `relation`-group.
        `pid` is entry, as in LOMv1.0's `relation.resource.identifier` category.
        """
        resource = {"identifier": [catalogify(pid, catalog="repo-pid")]}
        relation = {"kind": vocabularify(kind), "resource": resource}
        self.deduped_append("metadata.relation", relation)

    ###############
    #
    # methods for manipulating LOM's `classification` category
    #
    ###############

    def get_oefos_classification(self) -> dict:
        """Get the classification that holds OEFOS, create it if it didn't exist."""
        # oefos are part of the unique `classification` whose `purpose` is "discipline"
        # try to find that classification, otherwise create it
        for classification in self.record.get("metadata.classification", []):
            purpose = classification["purpose"]["value"]["langstring"]["#text"]
            if purpose == "discipline":
                return (oefos_classification := classification)

        # couldn't find; create oefos-classification-dict
        oefos_classification = {
            "purpose": vocabularify("discipline"),
            "taxonpath": [],
        }
        self.record["metadata.classification.[]"] = oefos_classification
        return oefos_classification

    def create_oefos_taxonpath(
        self, oefos_id: Union[str, int], language_code: str = "de"
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
            "source": langstringify("https://w3id.org/oerbase/vocabs/oefos2012"),
            "taxon": taxons,
        }

    def append_oefos_id(
        self, oefos_id: Union[str, int], language_code: str = "de"
    ) -> None:
        """Append a taxonpath corresponding to `oefos_id` to the oefos-classification.

        (The oefos-classification is the unique `classification` whose `purpose`
        is "discipline".)
        """
        taxonpaths = self.get_oefos_classification()["taxonpath"]
        new_taxonpath = self.create_oefos_taxonpath(oefos_id, language_code)

        # if a more comprehensive taxonpath already exists, don't add this one
        for old_taxonpath in taxonpaths:
            old_taxons = old_taxonpath["taxon"]
            new_taxons = new_taxonpath["taxon"]
            if all(taxon in old_taxons for taxon in new_taxons):
                # found previously existing taxonpath which holds a superset of
                # new taxons
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
        if new_taxonpath not in taxonpaths:
            taxonpaths.append(new_taxonpath)
