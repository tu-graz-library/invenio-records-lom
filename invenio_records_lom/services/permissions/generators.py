# -*- coding: utf-8 -*-
#
# Copyright (C) 2023-2026 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

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
