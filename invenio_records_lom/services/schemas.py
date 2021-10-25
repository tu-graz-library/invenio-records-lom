# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Marshmallow schema for validating and serializing LOM JSONs."""

from invenio_rdm_records.services.schemas import RDMParentSchema, RDMRecordSchema
from invenio_rdm_records.services.schemas.parent import ParentAccessSchema
from marshmallow import Schema, fields
from marshmallow_utils.fields import NestedAttribute


class LOMAgent(Schema):
    user = fields.Field(required=True)  # overwrite fields.Int, allow string-identities


class LOMParentAccessSchema(ParentAccessSchema):
    owned_by = fields.List(fields.Nested(LOMAgent))


class LOMParentSchema(RDMParentSchema):
    access = fields.Nested(LOMParentAccessSchema)


class LOMRecordSchema(RDMRecordSchema):

    # NOTE: To ensure compatibility with invenio systemfields,
    # use ``NestedAttribute`` instead of ``fields.Nested()``.

    # overwrite metadata-field: allow any dict
    metadata = fields.Dict(keys=fields.String(), values=fields.Field())
    # overwrite parent-field: allow string-users
    # TODO: write schema
    parent = NestedAttribute(LOMParentSchema, dump_only=True)


__all__ = ("LOMRecordSchema",)
