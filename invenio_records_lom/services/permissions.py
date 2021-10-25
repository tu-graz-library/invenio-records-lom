# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Permission-config classes for LOMRecordService-objects."""

from invenio_records_permissions.generators import AnyUser, Disable, SystemProcess
from invenio_records_permissions.policies.records import RecordPermissionPolicy


class LOMRecordPermissionPolicy(RecordPermissionPolicy):
    """Flask-principal style permissions for LOM record services.

    Note that the invenio_access.Permission class always adds ``superuser-access``,
    so admin-Identities are always allowed to take any action.
    """

    # TODO: settle permissions
    can_all = [AnyUser(), SystemProcess()]

    can_create = can_all
    can_edit = can_all
    can_publish = can_all
    can_update_draft = can_all

    #
    # Disabled actions (these should not be used or changed)
    #
    # - Records/files are updated/deleted via drafts so we don't support
    #   using below actions.
    can_update = [Disable()]
    can_delete = [Disable()]
    can_create_files = [Disable()]
    can_update_files = [Disable()]
    can_delete_files = [Disable()]
