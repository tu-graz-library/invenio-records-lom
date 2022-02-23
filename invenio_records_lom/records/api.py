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
from invenio_pidstore.models import PIDStatus
from invenio_records.systemfields import DictField, ModelField, RelationsField
from invenio_records_resources.records.api import FileRecord
from invenio_records_resources.records.systemfields import (
    FilesField,
    IndexField,
    PIDField,
    PIDStatusCheckField,
)

from . import models
from .systemfields import (
    LOMDraftRecordIdProvider,
    LOMPIDFieldContext,
    LOMRecordIdProvider,
    LOMResolver,
    ParentRecordAccessField,
    PIDLOMRelation,
    RecordAccessField,
)


class LOMParent(ParentRecord):
    """For representing entries from the 'lom_parents_metadata'-SQL-table."""

    model_cls = models.LOMParentMetadata

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

    model_cls = models.LOMFileDraftMetadata
    # LOMFileDraft and LOMDraft depend on each other, monkey-patch record_cls in later
    record_cls = None  # defined below


class LOMDraft(Draft):
    """For representing entries from the 'lom_drafts_metadata'-SQL-table."""

    model_cls = models.LOMDraftMetadata
    parent_record_cls = LOMParent
    versions_model_cls = models.LOMVersionsState

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
    index = IndexField("lomrecords-drafts-draft-v1.0.0", search_alias="lomrecords")
    is_published = PIDStatusCheckField(status=PIDStatus.REGISTERED, dump=True)
    pids = DictField()
    resource_type = DictField()


LOMFileDraft.record_cls = LOMDraft


class LOMFileRecord(FileRecord):
    """For representing entries from the 'lom_records_files_metadata'-SQL-table."""

    model_cls = models.LOMFileRecordMetadata
    # LOMFileRecord and LOMRecord depend on each other, monkey-patch this in later
    record_cls = None  # defined below


class RelationsMeta(type):
    """For self-referential `RelationsField`.

    Delays assigning to `.relations`' `pid_field` until class is already created.
    """

    def __new__(mcs, name, bases, attrs):
        """Create and return a new class with `.relations`-attribute."""
        cls = super().__new__(mcs, name, bases, attrs)
        relations = RelationsField(
            wholes=PIDLOMRelation(
                source="LOMv1.0",
                value="ispartof",
                pid_field=cls.pid,
                cache_key="lom-wholes",
            ),
            parts=PIDLOMRelation(
                source="LOMv1.0",
                value="haspart",
                pid_field=cls.pid,
                cache_key="lom-parts",
            ),
        )
        relations.__set_name__(cls, "relations")
        cls.relations = relations
        return cls


class LOMRecordMeta(type(Record), RelationsMeta):
    """Meta-Class for LOM-Records."""

    pass


class LOMRecord(Record, metaclass=LOMRecordMeta):
    """For representing entries from the 'lom_records_metadata'-SQL-table."""

    model_cls = models.LOMRecordMetadata
    parent_record_cls = LOMParent
    versions_model_cls = models.LOMVersionsState

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
    index = IndexField(
        "lomrecords-records-record-v1.0.0", search_alias="lomrecords-records"
    )
    is_published = PIDStatusCheckField(status=PIDStatus.REGISTERED, dump=True)
    pids = DictField()
    resource_type = DictField()


LOMFileRecord.record_cls = LOMRecord
