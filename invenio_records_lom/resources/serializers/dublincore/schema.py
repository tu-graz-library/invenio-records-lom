# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Global Search LOM schema."""

from flask_resources.serializers import BaseSerializerSchema
from marshmallow import fields

from ....utils import LOMMetadata


class LOMToDublinCoreRecordSchema(BaseSerializerSchema):
    """RDMRecordsSerializer."""

    contributors = fields.Method("get_contributors")
    titles = fields.Method("get_titles")
    creators = fields.Method("get_creators")
    identifiers = fields.Method("get_identifiers")
    relations = fields.Method("get_relations")
    rights = fields.Method("get_rights")
    dates = fields.Method("get_dates")
    subjects = fields.Method("get_subjects")
    descriptions = fields.Method("get_descriptions")
    publishers = fields.Method("get_publishers")
    types = fields.Method("get_types")
    sources = fields.Method("get_sources")
    languages = fields.Method("get_languages")
    locations = fields.Method("get_locations")
    formats = fields.Method("get_formats")

    def get_contributors(self, lom: LOMMetadata) -> list:
        """Get contributors."""
        return lom.get_contributors(name_only=True)

    def get_titles(self, lom: LOMMetadata) -> list:
        """Get titles."""
        return [lom.get_title(text_only=True)]

    def get_creators(self, lom: LOMMetadata) -> list:
        """Get creators."""
        return lom.get_contributors(name_only=True)

    def get_identifiers(self, lom: LOMMetadata) -> list:
        """Get identifiers."""
        return lom.get_identifiers(text_only=True)

    def get_relations(self, lom: LOMMetadata) -> list:
        """Get relations."""
        return lom.get_relations(text_only=True)

    def get_rights(self, lom: LOMMetadata) -> list:
        """Get rights."""
        return [lom.get_rights(url_only=True)]

    def get_dates(self, lom: LOMMetadata) -> list:
        """Get dates."""
        return lom.get_contributors(date_only=True)

    def get_subjects(self, lom: LOMMetadata) -> list:
        """Get subjects."""
        return lom.get_keywords(text_only=True)

    def get_descriptions(self, lom: LOMMetadata) -> list:
        """Get descriptions."""
        return lom.get_descriptions(text_only=True)

    def get_publishers(self, lom: LOMMetadata) -> list:
        """Get publishers."""
        return lom.get_contributors(name_only=True)

    def get_types(self, lom: LOMMetadata) -> list:
        """Get types."""
        return [lom.get_learning_resource_type(text_only=True)]

    def get_sources(self, _: LOMMetadata) -> list:
        """Get soruces."""
        return []

    def get_languages(self, lom: LOMMetadata) -> list:
        """Get languages."""
        return lom.get_languages()

    def get_locations(self, _: LOMMetadata) -> list:
        """Get locations."""
        return []

    def get_formats(self, lom: LOMMetadata) -> list:
        """Get formats."""
        return lom.get_formats()
