# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

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
