# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Schemas which get wrapped by serializers."""

from flask import current_app
from invenio_rdm_records.resources.serializers.ui.fields import AccessStatusField
from invenio_rdm_records.resources.serializers.ui.schema import (  # AdditionalDescriptionsSchema,; AdditionalTitlesSchema,; DatesSchema,; FormatEDTF,; L10NString,; RelatedIdentifiersSchema,; RightsSchema,; VocabularyL10Schema,; make_affiliation_index,; StrippedHTML,
    FormatDate,
    record_version,
)
from marshmallow import Schema, fields
from werkzeug.local import LocalProxy

from ...services.schemas.fields import ControlledVocabularyField


class LOMUIObjectSchema(Schema):
    """Schema for dumping additional data helpful for html-template creation."""

    created_date_l10n_long = FormatDate(attribute="created", format="long")

    updated_date_l10n_long = FormatDate(attribute="updated", format="long")

    resource_type = ControlledVocabularyField(
        attribute="resource_type",
        vocabulary=LocalProxy(lambda: current_app.config["LOM_RESOURCE_TYPES"]),
    )

    access_status = AccessStatusField(attribute="access")

    version = fields.Function(record_version)
