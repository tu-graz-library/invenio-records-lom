# SPDX-FileCopyrightText: 2021-2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Provider for LOM PID-fields."""

from invenio_drafts_resources.records.api import DraftRecordIdProviderV2
from invenio_pidstore.providers.recordid_v2 import RecordIdProviderV2


class LOMDraftRecordIdProvider(DraftRecordIdProviderV2):
    """PIDField provider for LOM drafts."""

    pid_type = "lomid"


class LOMRecordIdProvider(RecordIdProviderV2):
    """PIDField provider for LOM records."""

    pid_type = "lomid"
