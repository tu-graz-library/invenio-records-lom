# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Marshmallow schema for validating and serializing LOM JSONs."""

from invenio_rdm_records.services.schemas import RDMRecordSchema
from marshmallow import fields


class LOMRecordSchema(RDMRecordSchema):

    # NOTE: To ensure compatibility with invenio systemfields,
    # use ``NestedAttribute`` instead of ``fields.Nested()``.

    # overwrite metadata-field: allow any dict
    metadata = fields.Dict(keys=fields.String(), values=fields.Field())

    resource_type = fields.String()


__all__ = ("LOMRecordSchema",)
