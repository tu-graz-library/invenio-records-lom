# SPDX-FileCopyrightText: 2021-2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""LOM records - structures and represents database-information.

Follows the database-structure of invenio-rdm-records,
which - in turn - is based on the DataCite data model.
"""

from .api import LOMDraft, LOMFileDraft, LOMFileRecord, LOMParent, LOMRecord

__all__ = (
    "LOMDraft",
    "LOMFileDraft",
    "LOMFileRecord",
    "LOMParent",
    "LOMRecord",
)
