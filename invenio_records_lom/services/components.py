# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2024 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""LOM service components."""

from copy import copy

from flask_principal import Identity
from invenio_drafts_resources.records import Record
from invenio_drafts_resources.services.records.components import (
    DraftFilesComponent,
    PIDComponent,
    RelationsComponent,
    ServiceComponent,
)
from invenio_rdm_records.services.components import (
    AccessComponent,
    MetadataComponent,
    PIDsComponent,
)
from invenio_records_resources.services.uow import TaskOp

from ..records import LOMDraft, LOMRecord
from ..utils import LOMMetadata
from .tasks import register_or_update_pid


class ResourceTypeComponent(ServiceComponent):
    """Service component for resource_type.

    Akin to invenio_rdm_records.services.components.MetadataComponent.
    """

    new_version_skip_fields = ("publication_date", "version")

    def create(
        self,
        identity: Identity,  # noqa: ARG002
        data: dict | None = None,
        record: Record = None,
        **__: dict,
    ) -> None:
        """Inject parsed resource_type to the record."""
        record.resource_type = data.get("resource_type", {})

    def update_draft(
        self,
        identity: Identity,  # noqa: ARG002
        data: dict | None = None,
        record: Record = None,
        errors: list | None = None,  # noqa: ARG002
    ) -> None:
        """Inject parsed resource_type to the record."""
        record.resource_type = data.get("resource_type", {})

    def publish(
        self,
        identity: Identity,  # noqa: ARG002
        draft: Record = None,
        record: Record = None,
    ) -> None:
        """Update draft resource_type."""
        record.resource_type = draft.get("resource_type", {})

    def edit(
        self,
        identity: Identity,  # noqa: ARG002
        draft: Record = None,
        record: Record = None,
    ) -> None:
        """Update draft resource_type."""
        draft.resource_type = record.get("resource_type", {})

    def new_version(
        self,
        identity: Identity,  # noqa: ARG002
        draft: Record = None,
        record: Record = None,
    ) -> None:
        """Update draft resource_type."""
        draft.resource_type = copy(record.get("resource_type", {}))
        # Remove fields that should not be copied to the new version
        # (publication date and version)
        for f in self.new_version_skip_fields:
            draft.resource_type.pop(f, None)


class LOMPIDsComponent(PIDsComponent):
    """LOM Sevice component for PIDs."""

    def create(
        self,
        identity: Identity,
        data: dict | None = None,
        record: LOMDraft = None,
        errors: dict | None = None,
    ) -> None:
        """Add identifier to metadata on draft creation."""
        super().create(identity, data, record, errors)

        metadata = LOMMetadata(data["metadata"])
        metadata.append_identifier(record.pid.pid_value, catalog="repo-pid")
        record.metadata = metadata.json

    # overwrite `publish`` to use the celery-task from this package
    # this was copied from its parent class, except for its last line
    def publish(
        self,
        identity: Identity,  # noqa: ARG002
        draft: LOMDraft = None,
        record: LOMRecord = None,
    ) -> None:
        """Publish handler."""
        # ATTENTION: A draft can be for both an unpublished or published
        # record. For an unpublished record, we usually simply need to create
        # and reserve all PIDs. For a published record, some PIDs may allow
        # changes.

        # Extract all PIDs/schemes from the draft and the record
        draft_pids = draft.get("pids", {})
        record_pids = copy(record.get("pids", {}))
        draft_schemes = set(draft_pids.keys())
        record_schemes = set(record_pids.keys())

        # Determine schemes which are required, but not yet created.
        missing_required_schemes = (
            set(self.service.config.pids_required) - record_schemes - draft_schemes
        )

        # Validate the draft PIDs
        self.service.pids.pid_manager.validate(draft_pids, record, raise_errors=True)

        # Detect which PIDs on a published record that has been changed.
        #
        # Example: An external DOI (i.e. DOI not managed by us) can be changed
        # on a published record. Changes are handled by removing the old PID
        # and adding the new.
        changed_pids = {}
        for scheme in draft_schemes.intersection(record_schemes):
            record_id = record_pids[scheme]["identifier"]
            draft_id = draft_pids[scheme]["identifier"]
            if record_id != draft_id:
                changed_pids[scheme] = record_pids[scheme]

        self.service.pids.pid_manager.discard_all(changed_pids)

        # Create all PIDs specified on draft or which PIDs schemes which are
        # require
        pids = self.service.pids.pid_manager.create_all(
            draft,
            pids=draft_pids,
            schemes=missing_required_schemes,
        )

        # Reserve all created PIDs and store them on the record
        self.service.pids.pid_manager.reserve_all(draft, pids)
        record.pids = pids

        # Async register/update tasks after transaction commit.
        for scheme in pids:
            self.uow.register(TaskOp(register_or_update_pid, record["id"], scheme))


DefaultRecordsComponents = [
    MetadataComponent,
    AccessComponent,
    DraftFilesComponent,
    PIDComponent,
    LOMPIDsComponent,
    RelationsComponent,
    ResourceTypeComponent,
]
