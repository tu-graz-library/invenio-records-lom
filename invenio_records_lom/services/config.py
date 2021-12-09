# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Config classes for LOMRecordService-objects."""

from invenio_drafts_resources.services.records.components import (
    DraftFilesComponent,
    PIDComponent,
)
from invenio_drafts_resources.services.records.config import RecordServiceConfig
from invenio_rdm_records.services.components import (
    AccessComponent,
    MetadataComponent,
    RelationsComponent,
)
from invenio_records_resources.services import FileServiceConfig

from ..records import LOMDraft, LOMRecord
from .components import ResourceTypeComponent
from .permissions import LOMRecordPermissionPolicy
from .schemas import LOMRecordSchema


class LOMRecordServiceConfig(RecordServiceConfig):
    """Config for LOM record service."""

    schema = LOMRecordSchema

    draft_cls = LOMDraft
    record_cls = LOMRecord

    permission_policy_cls = LOMRecordPermissionPolicy

    components = [
        MetadataComponent,
        AccessComponent,
        DraftFilesComponent,
        PIDComponent,
        RelationsComponent,
        ResourceTypeComponent,
    ]


class LOMDraftFilesServiceConfig(FileServiceConfig):
    """Config for LOM draft files service."""

    record_cls = LOMDraft
    permission_action_prefix = "draft_"
    permission_policy_cls = LOMRecordPermissionPolicy

    file_links_list = {}
    file_links_item = {}


class LOMRecordFilesServiceConfig(FileServiceConfig):
    """Config for LOM files service."""

    record_cls = LOMRecord
    permission_policy_cls = LOMRecordPermissionPolicy

    file_links_list = {}
    file_links_item = {}
