# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

# NOTE: the containing folder and all its contents have been copied from
# invenio_rdm_records/services/components/ on (2021-08-29)

"""High-level API for working with RDM service components."""

from .access import AccessComponent
from .metadata import MetadataComponent
from .parent import ParentRecordAccessComponent
from .pids import ExternalPIDsComponent
from .relations import RelationsComponent

__all__ = (
    "AccessComponent",
    "ExternalPIDsComponent",
    "MetadataComponent",
    "ParentRecordAccessComponent",
    "RelationsComponent",
)
