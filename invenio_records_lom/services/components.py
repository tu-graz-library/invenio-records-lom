# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""LOM service components."""

from copy import copy

from invenio_drafts_resources.services.records.components import ServiceComponent


class ResourceTypeComponent(ServiceComponent):
    """Service component for resource_type.

    Akin to invenio_rdm_records.services.components.MetadataComponent.
    """

    new_version_skip_fields = ["publication_date", "version"]

    def create(self, identity, data=None, record=None, **kwargs):
        """Inject parsed resource_type to the record."""
        record.resource_type = data.get("resource_type", {})

    def update_draft(self, identity, data=None, record=None, **kwargs):
        """Inject parsed resource_type to the record."""
        record.resource_type = data.get("resource_type", {})

    def publish(self, identity, draft=None, record=None, **kwargs):
        """Update draft resource_type."""
        record.resource_type = draft.get("resource_type", {})

    def edit(self, identity, draft=None, record=None, **kwargs):
        """Update draft resource_type."""
        draft.resource_type = record.get("resource_type", {})

    def new_version(self, identity, draft=None, record=None, **kwargs):
        """Update draft resource_type."""
        draft.resource_type = copy(record.get("resource_type", {}))
        # Remove fields that should not be copied to the new version
        # (publication date and version)
        for f in self.new_version_skip_fields:
            draft.resource_type.pop(f, None)
