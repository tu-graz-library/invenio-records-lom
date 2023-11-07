# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Serializers turning records into html-template-insertable dicts."""
from collections.abc import Mapping
from copy import deepcopy

from flask_resources import BaseListSchema, JSONSerializer, MarshmallowSerializer
from lxml.builder import ElementMaker  # pylint: disable=no-name-in-module

from .schemas import LOMMetadataToOAISchema, LOMToDataCite44Schema, LOMUIRecordSchema


class LOMUIJSONSerializer(MarshmallowSerializer):
    """Wrapper with some convenience functions around a marshmallow-schema."""

    def __init__(self):
        """Initialize serializer with arguments for LOM-serialization."""
        super().__init__(
            format_serializer_cls=JSONSerializer,
            object_schema_cls=LOMUIRecordSchema,
            list_schema_cls=BaseListSchema,
            schema_context={"object_key": "ui"},
        )


class LOMToDataCite44Serializer(MarshmallowSerializer):
    """Marshmallow-based DataCite-serializer for LOM records."""

    def __init__(self, **kwargs):
        """Constructor."""
        super().__init__(
            format_serializer_cls=JSONSerializer,
            object_schema_cls=LOMToDataCite44Schema,
            **kwargs,
        )

    # TODO: Remove when invenio_rdm_records.services.pids.providers.datacite.DataCitePIDProvider
    # uses the new MarshmallowSerializer class
    def dump_one(self, obj):
        """Dump the object with extra information."""
        return self.dump_obj(obj)


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

    def __init__(self, metadata, lom_id, oaiserver_id_prefix, doi):
        """Constructor."""
        # metadata might be out of order, and includes extraneous fields
        # sort and filter with marshmallow:
        # TODO: clean some of this up in database rather than here
        metadata = deepcopy(metadata)
        if "lifeCycle" in metadata:
            # convert old capitalization to new one (note the capitalization of the 'C')
            metadata["lifecycle"] = metadata.pop("lifeCycle")
        if "metaMetadata" in metadata:
            # convert old capitalization to new one (note the capitalization of the second 'M')
            metadata["metametadata"] = metadata.pop("metaMetadata")
        try:
            self.metadata = LOMMetadataToOAISchema().load(metadata)
        except Exception:  # pylint: disable=broad-exception-caught
            self.metadata = metadata
        self.lom_id = lom_id
        self.oaiserver_id_prefix = oaiserver_id_prefix
        self.doi = doi
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

    @property
    def repository_doi_identifier(self):
        """Create the repository doi identifier."""
        jsn = {
            "catalog": "DOI",
            "entry": {
                "langstring": {
                    "lang": "x-none",
                    "#text": self.doi,
                }
            },
        }

        return [jsn]

    def build_langstring(self, jsn, parent_tag):
        """Append XML corresponding to `jsn` to `parent_tag`.

        `jsn` has to either be of form `{"lang": "lang-name", "#text": "any_text"}`,
        or be of form {"#text": "any_text"}.
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
            # while some of LOM-UIBK's examples include a type-attribute here, most don't
            # the `lom-uibk.xsd` also forbids extra attributes in this place...
        )
        parent_tag.append(tag)

    def build(self, jsn, parent_tag, inner_tag=None):
        """Walk through `jsn`, append its corresponding XML to `parent_tag`."""
        # `LOMMetadataToOAISchema` returns a mix of `dict`s and `OrderedDict`s, check against common parent-class `Mapping`
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
