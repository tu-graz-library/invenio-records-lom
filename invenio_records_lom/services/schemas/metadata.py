# -*- coding: utf-8 -*-
#
# Copyright (C) 202 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Marshmallow schema for validating and serializing LOM JSONs."""

from marshmallow import INCLUDE, Schema, fields, validate


class NoValidationSchema(Schema):
    """Let data through unchanged, without validation."""

    class Meta:
        """Configure this schema to include unknown fields no questions asked."""

        unknown = INCLUDE


class LangstringField(fields.Dict):
    """A dict-field of form {"langstring": {"#text": str, "lang": str}}."""

    default_error_messages = {
        "missing_langstring_key": "No {keys!r}-key in this langstring.",
        "extraneous_keys": "Extraneous keys in this langstring: {keys!r}.",
    }

    def _deserialize(self, value, attr, data, **kwargs):
        langstring_outer = super()._deserialize(value, attr, data, **kwargs)

        # validate outer keys
        outer_keys = set(langstring_outer)
        if "langstring" not in outer_keys:
            raise self.make_error("missing_langstring_key", keys="langstring")
        if not outer_keys <= {"langstring"}:
            raise self.make_error(
                "extraneous_keys", keys=sorted(outer_keys - {"langstring"})
            )

        langstring_inner = langstring_outer["langstring"]

        # validate inner keys
        if not isinstance(langstring_inner, dict):
            raise self.make_error("invalid")
        inner_keys = set(langstring_inner)
        if "#text" not in inner_keys:
            raise self.make_error("missing_langstring_key", keys="#text")
        if "lang" not in inner_keys:
            raise self.make_error("missing_langstring_key", keys="lang")
        if not inner_keys <= {"#text", "lang"}:
            raise self.make_error(
                "extraneous_keys", keys=sorted(inner_keys - {"#text", "lang"})
            )

        text = langstring_inner["#text"]
        lang = langstring_inner["lang"]

        # validate non-emptiness of "#text"-, "lang"-key
        if not text or not lang:
            raise self.make_error("required")

        return langstring_outer


class GeneralSchema(Schema):
    """Schema for LOM's `general` category."""

    class Meta:
        """Configure this schema to include unknown fields no questions asked."""

        unknown = INCLUDE

    title = LangstringField(required=True)
    keyword = fields.List(LangstringField)


class ContributeSchema(Schema):
    """Schema for LOM's contribute-fields."""

    role = fields.Dict()
    entity = fields.List(fields.String())


class LifecycleSchema(Schema):
    """Schema for Lom's `lifecycle category."""

    contribute = fields.List(
        fields.Nested(ContributeSchema()),
        validate=validate.Length(min=1, error="Enter at least one contribution."),
    )


class RightsSchema(Schema):
    """Schema for LOM's `rights`-category."""

    copyrightandotherrestrictions = fields.Dict()
    description = fields.Dict()
    url = fields.String(
        required=True,
        validate=validate.Length(min=1, error="Missing data for required field."),
    )


class MetadataSchema(Schema):
    """Schema for LOM-Metadata uploaded by deposit-page."""

    class Meta:
        """Configure this schema to include unknown fields no questions asked."""

        unknown = INCLUDE

    # passed by parent as to multiplex, removed by parent affter load/dump
    type = fields.Constant("upload")

    general = fields.Nested(GeneralSchema)
    lifecycle = fields.Nested(LifecycleSchema)
    rights = fields.Nested(RightsSchema)

    def load(self, data, **kwargs):
        """Overwrite parent as to use `NoValidationSchema` for resource-type!="upload"."""
        if data["type"] != "upload":
            return NoValidationSchema().load(data, **kwargs)
        data = super().load(data, **kwargs)
        return data

    def dump(self, obj, **_):
        """Overwrite parent as to dump everything always."""
        return obj
