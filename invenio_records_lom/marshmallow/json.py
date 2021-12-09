# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""JSON Schemas."""

from invenio_records_rest.schemas import StrictKeysMixin
from invenio_records_rest.schemas.fields import PersistentIdentifier, SanitizedUnicode
from marshmallow import fields


class LomMetadataSchemaV1(StrictKeysMixin):
    """Lom metadata."""

    id = PersistentIdentifier()
    name = SanitizedUnicode(required=True)
    organization = SanitizedUnicode(required=False)


class LomSchemaV1(StrictKeysMixin):
    """Lom schema."""

    metadata = fields.Nested(LomMetadataSchemaV1)
    created = fields.Str(dump_only=True)
    updated = fields.Str(dump_only=True)
    id = PersistentIdentifier()
