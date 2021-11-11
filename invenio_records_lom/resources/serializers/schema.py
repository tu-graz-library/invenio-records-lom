from invenio_rdm_records.resources.serializers.ui.fields import AccessStatusField
from invenio_rdm_records.resources.serializers.ui.schema import (  # AdditionalDescriptionsSchema,; AdditionalTitlesSchema,; DatesSchema,; FormatEDTF,; L10NString,; RelatedIdentifiersSchema,; RightsSchema,; VocabularyL10Schema,; make_affiliation_index,; StrippedHTML,
    FormatDate,
    record_version,
)
from marshmallow import Schema, fields


class LOMUIObjectSchema(Schema):
    created_date_l10n_long = FormatDate(attribute="created", format="long")

    updated_date_l10n_long = FormatDate(attribute="updated", format="long")

    resource_type = fields.String(attribute="resource_type")

    access_status = AccessStatusField(attribute="access")

    version = fields.Function(record_version)
