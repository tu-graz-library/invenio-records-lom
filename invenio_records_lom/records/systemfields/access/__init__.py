# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.


# NOTE: the containing folder and all its contents have been copied from
# invenio_rdm_records/records/systemfields/ on (2021-08-29)

"""Access system field for RDM Records."""

from .embargo import Embargo
from .field import (
    ParentRecordAccess,
    ParentRecordAccessField,
    RecordAccess,
    RecordAccessField,
)
from .grants import Grant, Grants
from .owners import Owner, Owners
from .protection import Protection

# from .links import Link, Links

__all__ = (
    "Embargo",
    "Grant",
    "Grants",
    "Owner",
    "Owners",
    "ParentRecordAccess",
    "ParentRecordAccessField",
    "Protection",
    "RecordAccess",
    "RecordAccessField",
)
