# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Serializers turning records into html-template-insertable dicts."""

from flask_resources.serializers import MarshmallowJSONSerializer
from invenio_rdm_records.resources.serializers import UIJSONSerializer
from lxml.builder import ElementMaker

from .schemas import LOMToDataCite44Schema, LOMUIObjectSchema


class LOMUIJSONSerializer(UIJSONSerializer):
    """Wrapper with some convenience functions around a marshmallow-schema."""

    object_schema_cls = LOMUIObjectSchema


class LOMToDataCite44Serializer(MarshmallowJSONSerializer):
    """Marshmallow-based DataCite-serializer for LOM records."""

    def __init__(self, **kwargs):
        """Constructor."""
        super().__init__(schema_cls=LOMToDataCite44Schema, **kwargs)


class LOMToLOMXMLSerializer:
    """Marshmallow-based LOM-XML serializer for LOM records."""

    NSMAP = {
        "lom": "https://oer-repo.uibk.ac.at/lom",
        "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    }
    ELEMENT_ATTRIBS = {
        f"{{{NSMAP['xsi']}}}schemaLocation": (
            "https://w3id.org/oerbase/profiles/lomuibk/latest/ "
            "https://w3id.org/oerbase/profiles/lomuibk/latest/lom-uibk.xsd"
        )
    }

    def __init__(self, metadata, lom_id, oaiserver_id_prefix):
        """Constructor."""
        self.metadata = metadata
        self.lom_id = lom_id
        self.oaiserver_id_prefix = oaiserver_id_prefix
        self.element_maker = ElementMaker(namespace=self.NSMAP["lom"], nsmap=self.NSMAP)

    @property
    def repository_identifier(self):
        """Create the repository identifier."""
        jsn = {
            "catalog": self.oaiserver_id_prefix,
            "entry": {
                "langstring": {
                    "lang": "x-none",
                    "#text": self.lom_id,
                }
            },
        }

        return [jsn]

    def build_langstring(self, jsn, parent_tag):
        """Append XML corresponding to `jsn` to `parent_tag`.

        `jsn` has to be of form `{"lang": "lang-name", "#text": "any_text"}`.
        """
        if "lang" in jsn:
            tag = self.element_maker.langstring(
                jsn["#text"],
                **{"{http://www.w3.org/XML/1998/namespace}lang": jsn["lang"]},
            )
        else:
            tag = self.element_maker.langstring(jsn["#text"])
        parent_tag.append(tag)

    def build_location(self, jsn, parent_tag):
        """Append location to parent_tag."""
        tag = self.element_maker.location(
            jsn["#text"],
            **{"{http://www.w3.org/XML/1998/namespace}lang": jsn["type"]},
        )
        parent_tag.append(tag)

    def build(self, jsn, parent_tag, inner_tag=None):
        """Walk through `jsn`, append its corresponding XML to `parent_tag`."""
        if isinstance(jsn, dict):
            for key, value in jsn.items():
                if key == "identifier":
                    lst = self.repository_identifier
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
                self.build(item, inner_tag)
                parent_tag.append(inner_tag)
        elif isinstance(jsn, str):
            parent_tag.text = jsn
        elif isinstance(jsn, int):
            parent_tag.text = str(jsn)
        else:
            raise ValueError(f"Unexpected value of type {type(jsn)} when building XML.")
        return parent_tag

    def serialize_object_xml(self):
        """Serialize a single record."""
        return self.build(self.metadata, self.element_maker.lom(**self.ELEMENT_ATTRIBS))


__all__ = (
    "LOMToDataCite44Serializer",
    "LOMToLOMXMLSerializer",
    "LOMUIJSONSerializer",
)
