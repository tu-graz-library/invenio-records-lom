# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Permission-config classes for LOMRecordService-objects."""

from invenio_records_permissions.generators import AnyUser
from invenio_records_permissions.policies.records import RecordPermissionPolicy


class LOMRecordPermissionPolicy(RecordPermissionPolicy):
    """Flask-principal style permissions for LOM record services.

    Note that the invenio_access.Permission class always adds ``superuser-access``,
    so admin-Identities are always allowed to take any action.
    """

    # TODO: settle permissions
    can_create = [AnyUser()]
    can_edit = [AnyUser()]
    can_publish = [AnyUser()]
    can_update_draft = [AnyUser()]
