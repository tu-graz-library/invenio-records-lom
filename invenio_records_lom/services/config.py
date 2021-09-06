# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Config classes for LOMRecordService-objects."""

from invenio_drafts_resources.services.records.components import PIDComponent
from invenio_drafts_resources.services.records.config import RecordServiceConfig

from .components import AccessComponent, MetadataComponent
from .permissions import LOMRecordPermissionPolicy
from .schemas import LOMRecordSchema


class LOMRecordServiceConfig(RecordServiceConfig):
    """Config for LOM record service."""

    schema = LOMRecordSchema

    permission_policy_cls = LOMRecordPermissionPolicy

    components = [
        MetadataComponent,
        AccessComponent,
        PIDComponent,
    ]
