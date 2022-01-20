# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Permission-config classes for LOMRecordService-objects."""

from invenio_rdm_records.services.generators import (
    IfRestricted,
    RecordOwners,
    SecretLinks,
)
from invenio_rdm_records.services.permissions import RDMRecordPermissionPolicy
from invenio_records_permissions.generators import (
    AnyUser,
    AuthenticatedUser,
    SystemProcess,
)


class LOMRecordPermissionPolicy(RDMRecordPermissionPolicy):
    """Flask-principal style permissions for LOM record services.

    Note that the invenio_access.Permission parent-class always adds
    ``superuser-access``, so admin-Identities are always allowed to take any action.
    """

    # no rights for CommunityCurators, as this package doesn't implement communities
    # no rights for SubmissionReviewers, as this package doesn't implement reviews
    can_manage = [RecordOwners(), SystemProcess()]
    can_curate = can_manage + [SecretLinks("edit")]
    can_review = can_curate
    can_preview = can_manage + [SecretLinks("preview")]
    can_view = can_manage + [SecretLinks("view")]

    can_authenticated = [AuthenticatedUser(), SystemProcess()]
    can_all = [AnyUser(), SystemProcess()]

    #
    #  Records
    #
    # Allow searching of records
    can_search = can_all
    # Allow reading metadata of a record
    can_read = [
        IfRestricted("record", then_=can_view, else_=can_all),
    ]
    # Allow reading the files of a record
    can_read_files = [
        IfRestricted("files", then_=can_view, else_=can_all),
    ]
    # Allow submitting new record
    can_create = can_authenticated

    #
    # Drafts
    #
    # Allow ability to search drafts
    can_search_drafts = can_authenticated
    # Allow reading metadata of a draft
    can_read_draft = can_preview
    # Allow reading files of a draft
    can_draft_read_files = can_preview
    # Allow updating metadata of a draft
    can_update_draft = can_review
    # Allow uploading, updating and deleting files in drafts
    can_draft_create_files = can_review
    can_draft_update_files = can_review
    can_draft_delete_files = can_review

    #
    # PIDs
    #
    can_pid_create = can_review
    can_pid_register = can_review
    can_pid_update = can_review
    can_pid_discard = can_review
    can_pid_delete = can_review

    #
    # Actions
    #
    # Allow to put a record in edit mode (create a draft from record)
    can_edit = can_curate
    # Allow deleting/discarding a draft and all associated files
    can_delete_draft = can_curate
    # Allow creating a new version of an existing published record.
    can_new_version = can_curate
    # Allow publishing a new record or changes to an existing record.
    can_publish = can_review
    # Allow lifting a record or draft.
    can_lift_embargo = can_manage
