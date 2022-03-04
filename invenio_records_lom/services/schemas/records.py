# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Marshmallow schema for validating and serializing LOM JSONs."""

from flask import current_app
from flask_babelex import lazy_gettext as _
from invenio_rdm_records.services.schemas import PIDSchema, RDMRecordSchema
from marshmallow import ValidationError, fields
from marshmallow_utils.fields import SanitizedUnicode
from werkzeug.local import LocalProxy

from .fields import ControlledVocabularyField


def validate_lom_scheme(scheme: str):
    """Validate whether scheme is supported."""
    if scheme not in current_app.config["LOM_PERSISTENT_IDENTIFIERS"]:
        raise ValidationError(_("Persistent identifier scheme unknown to LOM."))


class LOMRecordSchema(RDMRecordSchema):
    """Marshmallow schema for validating LOM records."""

    # NOTE: To ensure compatibility with invenio systemfields,
    # use ``NestedAttribute`` instead of ``fields.Nested()``.

    # overwrite metadata-field: allow any dict
    metadata = fields.Dict(keys=fields.String(), values=fields.Field())

    pids = fields.Dict(
        keys=SanitizedUnicode(validate=validate_lom_scheme),
        values=fields.Nested(PIDSchema),
    )

    resource_type = ControlledVocabularyField(
        vocabulary=LocalProxy(lambda: current_app.config["LOM_RESOURCE_TYPES"]),
    )


__all__ = ("LOMRecordSchema",)
