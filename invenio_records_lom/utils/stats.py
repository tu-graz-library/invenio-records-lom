# SPDX-FileCopyrightText: 2024-2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""statistic utils module."""


def build_record_unique_id(doc: dict) -> dict:
    """Build record unique identifier."""
    doc["unique_id"] = f"{doc['recid']}_{doc['parent_recid']}"
    return doc
