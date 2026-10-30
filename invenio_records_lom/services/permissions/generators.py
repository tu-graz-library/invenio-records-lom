# SPDX-FileCopyrightText: 2023-2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Permission generators for permission policies."""

from typing import cast

from flask import current_app
from invenio_records_permissions.generators import Generator


class OERCertifiedUsers(Generator):
    """Generates the `oer_certified_user` role-need."""

    def needs(self, **__: dict) -> list:
        """Generate needs to be checked against current user identity."""
        return cast(list, current_app.config.get("LOM_RECORD_CERTIFIED_USER_NEEDS", []))


class OERCurators(Generator):
    """Generates the `oer_curator` role-need."""

    def needs(self, **__: dict) -> list:
        """Generate needs to be checked against current user identity."""
        return cast(list, current_app.config.get("LOM_RECORD_CURATOR_USER_NEEDS", []))
