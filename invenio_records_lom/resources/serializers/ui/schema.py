# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2024 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Schemas for ui."""

from re import search
from types import MappingProxyType

from flask import current_app
from flask_resources import BaseObjectSchema
from invenio_rdm_records.resources.serializers.ui.fields import AccessStatusField
from invenio_rdm_records.resources.serializers.ui.schema import (
    FormatDate,
    record_version,
)
from marshmallow import fields
from marshmallow_oneofschema import OneOfSchema
from werkzeug.local import LocalProxy

from ....services.schemas.fields import ControlledVocabularyField
from ..utils import get_newest_part, get_related, get_text


class Title(fields.Field):
    """Title Field."""

    def _serialize(
        self,
        value,  # noqa: ANN001
        attr,  # noqa: ANN001, ARG002
        obj,  # noqa: ANN001, ARG002
        **kwargs: dict,  # noqa: ARG002
    ) -> str:
        """Serialize."""
        # TODO: checkout how to get the actual preferred language and show that
        # string if it exists!
        return get_text(value)


class Contributors(fields.Field):
    """Contributors Field."""

    def _serialize(
        self,
        value,  # noqa: ANN001
        attr,  # noqa: ANN001, ARG002
        obj,  # noqa: ANN001, ARG002
        **kwargs: dict,  # noqa: ARG002
    ) -> list[dict]:
        """Serialize."""
        return [
            {
                "fullname": sub_obj["entity"],
                "role": get_text(sub_obj["role"]["value"]),
            }
            for sub_obj in value
        ]


class GeneralDescriptions(fields.Field):
    """General Descriptions Field."""

    def _serialize(
        self,
        value,  # noqa: ANN001
        attr,  # noqa: ANN001, ARG002
        obj,  # noqa: ANN001, ARG002
        **kwargs: dict,  # noqa: ARG002
    ) -> None:
        """Serialize."""
        return list(map(get_text, value))


class EducationalDescriptions(fields.Field):
    """Educational Descriptions Field."""

    def _serialize(
        self,
        value,  # noqa: ANN001
        attr,  # noqa: ANN001, ARG002
        obj,  # noqa: ANN001, ARG002
        **kwargs: dict,  # noqa: ARG002
    ) -> None:
        """Serialize."""
        return list(map(get_text, value))


class Location(fields.Field):
    """Location Field."""

    def _serialize(
        self,
        value,  # noqa: ANN001
        attr,  # noqa: ANN001, ARG002
        obj,  # noqa: ANN001, ARG002
        **kwargs: dict,  # noqa: ARG002
    ) -> None:
        """Serialize."""
        return value["#text"]


class Rights(fields.Field):
    """Rights Field."""

    def _serialize(
        self,
        value,  # noqa: ANN001
        attr,  # noqa: ANN001, ARG002
        obj,  # noqa: ANN001, ARG002
        **kwargs: dict,  # noqa: ARG002
    ) -> None:
        """Serialize."""
        right = {}
        value = value or {}

        if "creativecommons" in value.get("url", ""):
            if "creativecommons.org/publicdomain/zero" in value["url"]:
                id_ = "CC0"
                icon = "cc-cc0-icon"
            else:
                result = search("licenses/([a-z-]+)/.*", value["url"])
                id_ = f"CC {result.group(1).upper()}"
                icon = f"{id_.lower().replace(' ', '-')}-icon"

            right = {
                "id": id_,
                "title_l10n": id_,
                "description_l10n": id_,
                "link": value["url"],
                "icon": icon,
            }

        return [right]


class LOMUIBaseSchema(BaseObjectSchema):
    """Base schema for LOMUI-classes, containing all common fields."""

    created_date_l10n_long = FormatDate(attribute="created", format="long")

    updated_date_l10n_long = FormatDate(attribute="updated", format="long")

    resource_type = ControlledVocabularyField(
        attribute="resource_type",
        vocabulary=LocalProxy(lambda: current_app.config["LOM_RESOURCE_TYPES"]),
    )

    access_status = AccessStatusField(attribute="access")

    version = fields.Function(record_version)

    title = Title(attribute="metadata.general.title")

    location = Location(attribute="metadata.technical.location")

    rights = Rights(attribute="metadata.rights")

    is_draft = fields.Boolean(attribute="is_draft")

    contributors = fields.Method("get_contributors")

    generalDescriptions = fields.Method("get_general_descriptions")  # noqa: N815

    educationalDescriptions = fields.Method(  # noqa: N815
        "get_educational_descriptions",
    )

    courses = fields.Method("get_courses")

    classifications = fields.Method("get_classifications")

    doi = fields.Method("get_doi")

    def get_contributors(self, obj: dict) -> list[dict]:
        """Get contributors."""
        ui_contributors = []
        for lom_contribute in (
            obj["metadata"].get("lifecycle", {}).get("contribute", [])
        ):
            for entity in lom_contribute.get("entity", []):
                ui_contributors.append(  # noqa: PERF401
                    {
                        "fullname": entity,
                        "role": get_text(lom_contribute["role"]["value"]),
                    },
                )
        return ui_contributors

    def get_general_descriptions(self, obj: dict) -> list[str]:
        """Get general descriptions."""
        return [
            get_text(desc)
            for desc in obj["metadata"].get("general", {}).get("description", [])
            if get_text(desc)
        ]

    def get_educational_descriptions(self, obj: dict) -> list[str]:
        """Get educational descriptions."""
        descriptions = obj["metadata"].get("educational", {}).get("description", [])
        if isinstance(descriptions, dict):
            # TODO: sometimes `metadata.educational.description` is made
            # :list[langstring], other times :langstring, unify this!
            descriptions = [descriptions]
        return [get_text(desc) for desc in descriptions if get_text(desc)]

    def get_courses(self, obj: dict) -> list[dict]:
        """Get courses."""
        courses = obj["metadata"].get("courses", [])
        return [
            {
                "title": get_text(course["course"]["title"]),
                "version": get_text(course["course"]["version"]),
            }
            for course in courses
        ]

    def get_classifications(self, obj: dict) -> list[str]:
        """Get classifications."""
        out = []

        for classification in obj["metadata"].get("classification", []):
            for taxon in classification.get("taxonpath", []):
                out.append(get_text(taxon["taxon"][-1]["entry"]))  # noqa: PERF401

        return out

    def get_doi(self, obj: dict) -> str:
        """Get DOI."""
        prefix = current_app.config["DATACITE_PREFIX"]
        pid = obj["id"]
        return f"https://doi.org/{prefix}/{pid}"


class LOMUILinkSchema(LOMUIBaseSchema):
    """Schema for dumping html-template data to a record of resource_type "link"."""


class LOMUIFileSchema(LOMUIBaseSchema):
    """Schema for dumping html-template data to a record of resource_type "file"."""


class LOMUIUnitSchema(LOMUIBaseSchema):
    """Schema for dumping html-template data to a record of resource_type "unit"."""


class LOMUICourseSchema(LOMUIBaseSchema):
    """Schema for dumping html-template data to a record of resource_type "course"."""

    def get_contributors(self, obj: dict) -> list[dict]:
        """Get contributors, overwrites parent-class's `get_contributors`."""
        # courses don't store contribution-information, try to get from
        # associated unints instead
        ui_contributors = []
        for unit in get_related(obj, relation_kind="haspart"):
            if "metadata" not in unit:
                # in this case, relations of obj have not been dereferenced
                # can happen e.g. when called with obj directly from opensearch
                continue
            ui_contributors.extend(super().get_contributors(unit))

        return ui_contributors

    def get_general_descriptions(self, obj: dict) -> list[str]:
        """Get general descriptions.

        Overwrite parent-class's `get_general_descriptions`.
        """
        # courses don't store description-information, try to get from newest
        # associated unit instead
        newest_unit = get_newest_part(obj)
        if "metadata" not in newest_unit:
            # in this case, relations of obj have not been dereferenced
            # can happen e.g. when called with obj directly from opensearch
            return []
        return super().get_general_descriptions(newest_unit)

    def get_educational_descriptions(self, obj: dict) -> list[str]:
        """Get educational descriptions.

        Overwrite parent-class's `get_educational_descriptions`.
        """
        # courses don't store description-information, try to get from newest
        # associated unit instead
        newest_unit = get_newest_part(obj)
        if "metadata" not in newest_unit:
            # in this case, relations of obj have not been dereferenced
            # can happen e.g. when called with obj directly from opensearch
            return []
        return super().get_educational_descriptions(newest_unit)


class LOMUIUploadSchema(LOMUIFileSchema):
    """Schema for dumping html-template data to a record of resource_type "upload"."""


class LOMUIRecordSchema(OneOfSchema):
    """Delegates to different schemas.

    Depending on data_to_serialize["resource_type"]
    """

    type_field = "resource_type"
    type_schemas = MappingProxyType(
        {
            "file": LOMUIFileSchema,
            "unit": LOMUIUnitSchema,
            "course": LOMUICourseSchema,
            "link": LOMUILinkSchema,
            "upload": LOMUIUploadSchema,
        },
    )

    def get_obj_type(self, obj: dict) -> str:
        """Get type of `obj`.

        Which is used as a key to look up a schema within type_schemas
        """
        return obj["resource_type"]
