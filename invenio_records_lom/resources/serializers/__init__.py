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
    E_attribs = {
        f"{{{NSMAP['xsi']}}}schemaLocation": (
            "https://w3id.org/oerbase/profiles/lomuibk/latest/ "
            "https://w3id.org/oerbase/profiles/lomuibk/latest/lom-uibk.xsd"
        )
    }

    def __init__(self, **options):
        """Constructor."""
        self._schema_cls = None

        self.E = ElementMaker(namespace=self.NSMAP["lom"], nsmap=self.NSMAP)

    def build_langstring(self, jsn, parent_tag):
        """Append XML corresponding to `jsn` to `parent_tag`.

        `jsn` has to be of form `{"lang": "lang-name", "#text": "any_text"}`.
        """
        if "lang" in jsn:
            tag = self.E.langstring(
                jsn["#text"],
                **{"{http://www.w3.org/XML/1998/namespace}lang": jsn["lang"]},
            )
        else:
            tag = self.E.langstring(jsn["#text"])
        parent_tag.append(tag)

    def build(self, jsn, parent_tag):
        """Walk through `jsn`, append its corresponding XML to `parent_tag`."""
        if isinstance(jsn, dict):
            for k, v in jsn.items():
                if k == "langstring":
                    self.build_langstring(v, parent_tag)
                    continue
                lst = v if isinstance(v, list) else [v]
                for item in lst:
                    inner_tag = self.E(k.lower())
                    self.build(item, inner_tag)
                    parent_tag.append(inner_tag)
        elif isinstance(jsn, str):
            parent_tag.text = jsn
        else:
            raise ValueError(f"Unexpected value of type {type(jsn)} when building XML.")
        return parent_tag

    def serialize_object_xml(self, obj):
        """Serialize a single record."""
        return self.build(obj["metadata"], self.E.lom(**self.E_attribs))


__all__ = (
    "LOMToDataCite44Serializer",
    "LOMToLOMXMLSerializer",
    "LOMUIJSONSerializer",
)
