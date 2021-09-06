# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""SQL-table definitions for LOM module."""

from invenio_db import db
from invenio_drafts_resources.records import (
    DraftMetadataBase,
    ParentRecordMixin,
    ParentRecordStateMixin,
)
from invenio_files_rest.models import Bucket
from invenio_records.models import RecordMetadataBase
from invenio_records_resources.records.models import FileRecordModelMixin
from sqlalchemy_utils.types import UUIDType


class LOMParentMetadata(db.Model, RecordMetadataBase):
    """Flask-SQLAlchemy model for "lom_parents_metadata"-SQL-table."""

    __tablename__ = "lom_parents_metadata"


class LOMDraftMetadata(db.Model, DraftMetadataBase, ParentRecordMixin):
    """Flask-SQLAlchemy model for "lom_drafts_metadata"-SQL-table."""

    __tablename__ = "lom_drafts_metadata"

    # ParentRecordMixin adds to __parent_record_model__ a foreign key to self
    __parent_record_model__ = LOMParentMetadata

    bucket_id = db.Column(UUIDType, db.ForeignKey(Bucket.id))
    bucket = db.relationship(Bucket)


class LOMFileDraftMetadata(db.Model, RecordMetadataBase, FileRecordModelMixin):
    """Flask-SQLAlchemy model for "lom_drafts_files"-SQL-table."""

    __tablename__ = "lom_drafts_files"

    __record_model_cls__ = LOMDraftMetadata


class LOMRecordMetadata(db.Model, RecordMetadataBase, ParentRecordMixin):
    """Flask-SQLAlchemy model for "lom_records_metadata"-SQL-table."""

    __tablename__ = "lom_records_metadata"

    __parent_record_model__ = LOMParentMetadata

    # signals SQLAlchemy-Continuum to record transactions with this table
    # other models keep track of versions with their `version_id`-attribute
    __versioned__ = {}

    bucket_id = db.Column(UUIDType, db.ForeignKey(Bucket.id))
    bucket = db.relationship(Bucket)


class LOMFileRecordMetadata(db.Model, RecordMetadataBase, FileRecordModelMixin):
    """Flask-SQLAlchemy model for "lom_records_files"-SQL-table."""

    __tablename__ = "lom_records_files"

    __record_model_cls__ = LOMRecordMetadata

    __versioned__ = {}


class LOMVersionsState(db.Model, ParentRecordStateMixin):
    """Flask-SQLAlchemy model for "lom_versions_state"-SQL-table."""

    __tablename__ = "lom_versions_state"

    __parent_record_model__ = LOMParentMetadata
    __record_model__ = LOMRecordMetadata
    __draft_model__ = LOMDraftMetadata
