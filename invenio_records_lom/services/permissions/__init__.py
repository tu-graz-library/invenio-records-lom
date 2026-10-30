# SPDX-FileCopyrightText: 2023-2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Permission-policy and roles, based on `flask-principal`."""

from .generators import OERCertifiedUsers, OERCurators
from .policy import LOMRecordPermissionPolicy

__all__ = (
    "LOMRecordPermissionPolicy",
    "OERCertifiedUsers",
    "OERCurators",
)
