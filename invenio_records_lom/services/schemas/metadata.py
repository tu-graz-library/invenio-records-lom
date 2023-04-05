# -*- coding: utf-8 -*-
#
# Copyright (C) 202 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Marshmallow schema for validating and serializing LOM JSONs."""

import copy

from marshmallow import INCLUDE, Schema, fields, validate


class NoValidationSchema(Schema):
    """Let data through unchanged, without validation."""

    class Meta:
        """Configure this schema to include unknown fields no questions asked."""

        unknown = INCLUDE

    def dump(self, obj, **_):
        """Overwrite dump to return `obj`, bypassing validation as class name indicates."""
        return copy.copy(obj)


class LangstringField(fields.Field):
    """Verifies against form {"langstring": {"#text": str, "lang": str}}."""

    default_error_messages = {
        "extraneous_keys": "Extraneous keys in this langstring: {keys!r}.",
        "extraneous_lang": "This Langstring must not have a `lang`-field.",
        "missing_langstring_key": "No {keys!r}-key in this langstring.",
    }

    def __init__(self, lang_exists=True, **kwargs):
        """Init."""
        super().__init__(**kwargs)
        self.lang_exists = lang_exists

    def _deserialize(self, value, attr, data, **kwargs):
        if not isinstance(value, dict):
            raise self.make_error("invalid")

        # validate outer keys
        outer_keys = set(value)
        if "langstring" not in outer_keys:
            raise self.make_error("missing_langstring_key", keys="langstring")
        if not outer_keys <= {"langstring"}:
            raise self.make_error(
                "extraneous_keys", keys=sorted(outer_keys - {"langstring"})
            )

        langstring_inner = value["langstring"]

        # validate inner keys
        if not isinstance(langstring_inner, dict):
            raise self.make_error("invalid")
        inner_keys = set(langstring_inner)
        if "#text" not in inner_keys:
            raise self.make_error("missing_langstring_key", keys="#text")
        if "lang" not in inner_keys and self.lang_exists:
            raise self.make_error("missing_langstring_key", keys="lang")
        if "lang" in inner_keys and not self.lang_exists:
            raise self.make_error("extraneous_lang")
        if not inner_keys <= {"#text", "lang"}:
            raise self.make_error(
                "extraneous_keys", keys=sorted(inner_keys - {"#text", "lang"})
            )

        text = langstring_inner["#text"]
        lang = langstring_inner.get("lang", True)

        # validate non-emptiness of "#text"-, "lang"-key
        if not text or not lang:
            raise self.make_error("required")

        return value


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
    entity = fields.List(
        fields.String(validate=validate.Length(min=1, error="Name cannot be empty."))
    )


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


class TaxonSchema(Schema):
    """Schema for Lom's `classification.taxonpath.taxon`-category."""

    id = fields.String(
        required=True,
        validate=validate.Regexp(
            r"https://w3id.org/oerbase/vocabs/oefos2012/\d+",
            error="Not a valid OEFOS-url.",
        ),
    )
    entry = LangstringField(lang_exists=False)


class TaxonpathSchema(Schema):
    """Schema for LOM's `classification.taxonpath`-category."""

    source = fields.Field(
        required=True,
        validate=validate.Equal(
            {
                "langstring": {
                    "#text": "https://w3id.org/oerbase/vocabs/oefos2012",
                    "lang": "x-none",
                }
            }
        ),
    )
    taxon = fields.Nested(
        TaxonSchema,
        many=True,
        required=True,
        validate=validate.Length(
            min=1, error="Must add at least one taxonomy to OEFOS taxonomy-path."
        ),
    )


class ClassificationSchema(Schema):
    """Schema for LOM's `classification`-category."""

    purpose = fields.Field(
        required=True,
        validate=validate.Equal(
            {
                "source": {"langstring": {"#text": "LOMv1.0", "lang": "x-none"}},
                "value": {"langstring": {"#text": "discipline", "lang": "x-none"}},
            }
        ),
    )
    taxonpath = fields.Nested(
        TaxonpathSchema,
        many=True,
        required=True,
        validate=validate.Length(min=1, error="Must add at least one OEFOS."),
    )


class MetadataSchema(Schema):
    """Schema for LOM-Metadata uploaded by deposit-page."""

    class Meta:
        """Configure this schema to include unknown fields no questions asked."""

        unknown = INCLUDE

    # passed by parent as to multiplex, removed by parent affter load/dump
    type = fields.Field(validate=validate.Equal("upload"))

    general = fields.Nested(GeneralSchema, required=True)
    lifecycle = fields.Nested(LifecycleSchema, required=True)
    rights = fields.Nested(RightsSchema, required=True)
    classification = fields.Nested(
        ClassificationSchema,
        many=True,
        required=True,
        validate=validate.Length(min=1, error="Must add OEFOS-classification."),
    )

    def load(self, data, **kwargs):
        """Overwrite parent as to use `NoValidationSchema` for resource-type!="upload"."""
        if data["type"] != "upload":
            return NoValidationSchema().load(data, **kwargs)
        data = super().load(data, **kwargs)
        return data

    def dump(self, obj, **_):
        """Overwrite parent as to dump everything always."""
        return obj
