# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Permission-policy and roles, based on `flask-principal`."""

from .generators import OERCertifiedUsers, OERCurators
from .policy import LOMRecordPermissionPolicy

__all__ = (
    "LOMRecordPermissionPolicy",
    "OERCertifiedUsers",
    "OERCurators",
)
