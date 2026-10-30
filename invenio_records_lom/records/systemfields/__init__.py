# SPDX-FileCopyrightText: 2021-2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""LOM System Fields.

System Fields execute actions on creating, editing, publishing, ... the
API-object they are attributes of.
"""

from invenio_rdm_records.records.systemfields import (
    ParentRecordAccessField,
    RecordAccessField,
)

from .context import LOMPIDFieldContext
from .providers import LOMDraftRecordIdProvider, LOMRecordIdProvider
from .relations import PIDLOMRelation
from .resolver import LOMResolver
from .stats import LomRecordStatisticsField

__all__ = (
    "LOMDraftRecordIdProvider",
    "LOMPIDFieldContext",
    "LOMRecordIdProvider",
    "LOMResolver",
    "LomRecordStatisticsField",
    "PIDLOMRelation",
    "ParentRecordAccessField",
    "RecordAccessField",
)
