# SPDX-FileCopyrightText: 2021-2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Record services configured for LOM-use."""

from invenio_rdm_records.services import RDMRecordService


class LOMRecordService(RDMRecordService):
    """RecordService configured for LOM-use."""
