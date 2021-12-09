# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""High-level API for working with LOM records, files, pids and search."""

from .config import (
    LOMDraftFilesServiceConfig,
    LOMRecordFilesServiceConfig,
    LOMRecordServiceConfig,
)
from .permissions import LOMRecordPermissionPolicy
from .services import LOMRecordService

__all__ = (
    "LOMDraftFilesServiceConfig",
    "LOMRecordPermissionPolicy",
    "LOMRecordFilesServiceConfig",
    "LOMRecordService",
    "LOMRecordServiceConfig",
)
