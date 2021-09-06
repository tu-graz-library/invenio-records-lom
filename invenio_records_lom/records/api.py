# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Classes for "API"-objects, whose fields represent database-information.

Use flask.current_app['invenio-records-lom'].records_service to interact with.
"""

# fields execute actions on creating, editing, publishing, ... the object
# Some possibly useful fields are:
# dumper =  # overwrite to add extensions to elasticsearch dumper,
#     e.g. adding EDTF-support
#     cf invenio_rdm_records.records.dumpers
# is_published =  # overwrite with PIDStatusCheckField(dump=True) to:
#     delete from api-object on dump and add back to api-object on load
# has_draft =  # needed to lift embargos
# pids =  # add further pids from data['pids'],
#     use with ExternalPIDsComponent
# parent =  # change create, soft_delete, hard_delete
# relations =  # validate then clean assigned relations
# schema =  # add second validation via jsonschema

from invenio_drafts_resources.records import Draft, Record
from invenio_drafts_resources.records.api import ParentRecord
from invenio_records.systemfields import ModelField
from invenio_records_resources.records.api import FileRecord
from invenio_records_resources.records.systemfields import (
    FilesField,
    IndexField,
    PIDField,
)
from werkzeug.local import LocalProxy

from .systemfields import (
    LOMDraftRecordIdProvider,
    LOMPIDFieldContext,
    LOMRecordIdProvider,
    LOMResolver,
    ParentRecordAccessField,
    RecordAccessField,
)


class LOMParent(ParentRecord):
    """For representing entries from the 'lom_parents_metadata'-SQL-table."""

    pid = PIDField(
        key="id",
        provider=LOMDraftRecordIdProvider,
        resolver_cls=LOMResolver,
        context_cls=LOMPIDFieldContext,
        # flag for deleting pid from database on post-record-deletion,
        # pid is deleted via LOMRecordService instead
        delete=False,
    )
    access = ParentRecordAccessField()


class LOMFileDraft(FileRecord):
    """For representing entries from the 'lom_drafts_files'-SQL-table."""

    # LOMFileDraft and LOMDraft depend on each other, delay name-lookup to accomodate
    record_cls = LocalProxy(lambda: LOMDraft)


class LOMDraft(Draft):
    """For representing entries from the 'lom_drafts_metadata'-SQL-table."""

    parent_record_cls = LOMParent

    pid = PIDField(
        key="id",
        provider=LOMDraftRecordIdProvider,
        resolver_cls=LOMResolver,
        context_cls=LOMPIDFieldContext,
        # flag for deleting pid from database on post-record-deletion,
        # delete pid via LOMRecordService instead
        delete=False,
    )
    files = FilesField(
        file_cls=LOMFileDraft,
        delete=False,
        store=False,
    )
    access = RecordAccessField()
    bucket_id = ModelField(dump=False)
    bucket = ModelField(dump=False)
    index = IndexField("lomrecords-drafts-v1.0.0", search_alias="lomrecords")


class LOMFileRecord(FileRecord):
    """For representing entries from the 'lom_records_files_metadata'-SQL-table."""

    # LOMFileRecord and LOMRecord depend on each other, delay name-lookup to accomodate
    record_cls = LocalProxy(lambda: LOMDraft)


class LOMRecord(Record):
    """For representing entries from the 'lom_records_metadata'-SQL-table."""

    parent_record_cls = LOMParent

    pid = PIDField(
        key="id",
        provider=LOMRecordIdProvider,
        resolver_cls=LOMResolver,
        context_cls=LOMPIDFieldContext,
        # flag for deleting pid from database on post-record-deletion,
        # delete pid via LOMRecordService instead
        delete=False,
    )
    files = FilesField(
        file_cls=LOMFileRecord,
        create=False,
        delete=False,
        store=False,
    )
    access = RecordAccessField()
    bucket_id = ModelField(dump=False)
    bucket = ModelField(dump=False)
    index = IndexField("lomrecords-records-v1.0.0", search_alias="lomrecords")
