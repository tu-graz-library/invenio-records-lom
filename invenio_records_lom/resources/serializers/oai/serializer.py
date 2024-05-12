# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""OAI serializer."""

from collections.abc import Mapping
from copy import deepcopy
from types import MappingProxyType

from flask import current_app
from lxml.builder import ElementMaker
from lxml.etree import Element

from .schema import LOMToOAISchema


class LOMToOAIXMLSerializer:
    """Marshmallow-based LOM-XML serializer for LOM records."""

    NSMAP = MappingProxyType(
        {
            "lom": "https://oer-repo.uibk.ac.at/lom",
            "xsi": "http://www.w3.org/2001/XMLSchema-instance",
        },
    )
    ELEMENT_ATTRIBS = MappingProxyType(
        {
            f"{{{NSMAP['xsi']}}}schemaLocation": (
                "https://w3id.org/oerbase/profiles/lomuibk/latest/ "
                "https://w3id.org/oerbase/profiles/lomuibk/latest/lom-uibk.xsd"
            ),
        },
    )

    def __init__(
        self,
        metadata: dict,
        lom_id: str,
        oaiserver_id_prefix: str,
        doi: str,
    ) -> None:
        """Construct."""
        # metadata might be out of order, and includes extraneous fields
        # sort and filter with marshmallow:
        # TODO: clean some of this up in database rather than here
        metadata = deepcopy(metadata)

        if "lifeCycle" in metadata:
            # convert old capitalization to new one (note the capitalization of the 'C')
            metadata["lifecycle"] = metadata.pop("lifeCycle")

        if "metaMetadata" in metadata:
            # convert old capitalization to new one (note the capitalization of
            # the second 'M')
            metadata["metametadata"] = metadata.pop("metaMetadata")

        try:
            self.metadata = LOMToOAISchema().dump(metadata)
        except Exception:  # noqa: BLE001
            self.metadata = metadata

        self.lom_id = lom_id
        self.oaiserver_id_prefix = oaiserver_id_prefix
        self.doi = doi
        self.element_maker = ElementMaker(namespace=self.NSMAP["lom"], nsmap=self.NSMAP)

    @property
    def repository_identifier(self) -> list[dict]:
        """Create the repository identifier."""
        jsn = {
            "catalog": self.oaiserver_id_prefix,
            "entry": {
                "langstring": {
                    "lang": "x-none",
                    "#text": self.lom_id,
                },
            },
        }

        return [jsn]

    @property
    def repository_doi_identifier(self) -> list[dict]:
        """Create the repository doi identifier."""
        if self.doi is None:
            return []

        jsn = {
            "catalog": "DOI",
            "entry": {
                "langstring": {
                    "lang": "x-none",
                    "#text": self.doi,
                },
            },
        }

        return [jsn]

    def build_langstring(self, jsn: dict, parent_tag: Element) -> None:
        """Append XML corresponding to `jsn` to `parent_tag`.

        `jsn` has to either be of form `{"lang": "lang-name", "#text": "any_text"}`,
        or be of form {"#text": "any_text"}.
        """
        if "lang" not in jsn:
            jsn["lang"] = "x-none"

        try:
            tag = self.element_maker.langstring(
                jsn["#text"],
                **{"{http://www.w3.org/XML/1998/namespace}lang": jsn["lang"]},
            )
        except ValueError:
            current_app.logger.exception("ERROR LOM oai lom pid: %s", self.lom_id)
            tag = self.element_maker.langstring(
                "N/A",
                **{"{http://www.w3.org/XML/1998/namespace}lang": "x-none"},
            )

        parent_tag.append(tag)

    def build_location(self, jsn: dict, parent_tag: Element) -> None:
        """Append location to parent_tag."""
        tag = self.element_maker.location(
            jsn["#text"],
            # while some of LOM-UIBK's examples include a type-attribute here,
            # most don't the `lom-uibk.xsd` also forbids extra attributes in
            # this place...
        )
        parent_tag.append(tag)

    def build(  # noqa: C901
        self,
        jsn: dict,
        parent_tag: Element,
        inner_tag: Element = None,
    ) -> Element:
        """Walk through `jsn`, append its corresponding XML to `parent_tag`."""
        # `LOMToOAISchema` returns a mix of `dict`s and `OrderedDict`s, check
        # against common parent-class `Mapping`
        if isinstance(jsn, Mapping):
            for key, value in jsn.items():
                if key == "identifier":
                    for lst in [
                        self.repository_identifier,
                        self.repository_doi_identifier,
                    ]:
                        self.build(lst, parent_tag, self.element_maker("identifier"))

                if key == "langstring":
                    self.build_langstring(value, parent_tag)
                elif key == "location":
                    self.build_location(value, parent_tag)
                else:
                    lst = value if isinstance(value, list) else [value]
                    self.build(lst, parent_tag, self.element_maker(key.lower()))
        elif isinstance(jsn, list):
            for item in jsn:
                local_tag = deepcopy(inner_tag)
                self.build(item, local_tag)
                parent_tag.append(local_tag)
        elif isinstance(jsn, str):
            parent_tag.text = jsn
        elif isinstance(jsn, int):
            parent_tag.text = str(jsn)
        else:
            msg = f"Unexpected value of type {type(jsn)} when building XML."
            raise TypeError(msg)
        return parent_tag

    def dump_obj(self) -> Element:
        """Serialize a single record."""
        return self.build(self.metadata, self.element_maker.lom(**self.ELEMENT_ATTRIBS))
