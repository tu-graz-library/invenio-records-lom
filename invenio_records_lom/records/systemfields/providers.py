# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Provider for LOM PID-fields."""

from invenio_drafts_resources.records.api import DraftRecordIdProviderV2
from invenio_pidstore.providers.recordid_v2 import RecordIdProviderV2


class LOMDraftRecordIdProvider(DraftRecordIdProviderV2):
    """PIDField provider for LOM drafts."""

    pid_type = "lomid"


class LOMRecordIdProvider(RecordIdProviderV2):
    """PIDField provider for LOM records."""

    pid_type = "lomid"
