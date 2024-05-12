# -*- coding: utf-8 -*-
#
# Copyright (C) 2023-2024 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Permission generators for permission policies."""

from invenio_records_permissions.generators import Generator

from .roles import oer_certified_user, oer_curator


class OERCertifiedUsers(Generator):
    """Generates the `oer_certified_user` role-need."""

    def needs(self, **__: dict) -> list:
        """Generate needs to be checked against current user identity."""
        return [oer_certified_user]


class OERCurators(Generator):
    """Generates the `oer_curator` role-need."""

    def needs(self, **__: dict) -> list:
        """Generate needs to be checked against current user identity."""
        return [oer_curator]
