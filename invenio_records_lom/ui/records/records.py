# -*- coding: utf-8 -*-
#
# Copyright (C) 2019-2021 CERN.
# Copyright (C) 2019-2021 Northwestern University.
# Copyright (C)      2021 TU Wien.
# Copyright (C) 2021-2022 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
# For the original code see the NOTE below.


# NOTE:
# copy-pasted code from invenio_app_rdm/records_ui/views/decorators.py
# copy-pasting was necessary to overrride the standard-behavior with custom behavior

"""View-functions for record-related pages."""

import typing as t
from os.path import splitext

from flask import abort, current_app, redirect, render_template, request, url_for
from invenio_base.utils import obj_or_import_string
from invenio_previewer.extensions import default
from invenio_previewer.proxies import current_previewer
from invenio_records_resources.services.files.results import FileItem, FileList
from invenio_records_resources.services.records.results import RecordItem

from ...resources.serializers import LOMUIJSONSerializer
from .decorators import (
    pass_file_item,
    pass_file_metadata,
    pass_is_preview,
    pass_record_files,
    pass_record_from_pid,
    pass_record_latest,
    pass_record_or_draft,
)


class PreviewFile:
    """Preview file implementation for InvenioRDM.

    This class was apparently created because of subtle differences with
    `invenio_previewer.api.PreviewFile`.
    """

    def __init__(self, file_item: FileItem, record_pid_value: str, url: str = None):
        """Create a new PreviewFile."""
        self.file = file_item
        self.data = file_item.data
        self.size = self.data["size"]
        self.filename = self.data["key"]
        self.bucket = self.data["bucket_id"]
        self.uri = url or url_for(
            "invenio_app_rdm_records.record_file_download",
            pid_value=record_pid_value,
            filename=self.filename,
        )

    def is_local(self):
        """Check if file is local."""
        return True

    def has_extensions(self, *exts):
        """Check if file has one of the extensions.

        Each `exts` has the format `.{file type}` e.g. `.txt` .
        """
        file_ext = splitext(self.data["key"])[1].lower()
        return file_ext in exts

    def open(self):
        """Open the file."""
        return self.file._file.file.storage().open()


#
# Views
#
@pass_is_preview
@pass_record_or_draft
@pass_record_files
def record_detail(
    pid_value: str = None,
    is_preview: bool = None,
    record: RecordItem = None,
    files: t.Optional[FileList] = None,
):
    """Record detail page (aka landing page)."""
    files_dict = {} if files is None else files.to_dict()
    record_ui = LOMUIJSONSerializer().serialize_object_to_dict(record.to_dict())

    if is_preview and record._record.is_draft:
        abort(404)

    return render_template(
        "invenio_records_lom/record.html",
        record=record_ui,
        pid=pid_value,
        files=files_dict,
        permissions=record.has_permissions_to(
            ["edit", "new_version", "manage", "update_draft", "read_files"]
        ),
        is_preview=is_preview,
        is_draft=record._record.is_draft,
    )


@pass_is_preview
@pass_record_or_draft
def record_export(
    record: RecordItem = None,
    export_format: str = None,
    pid_value: str = None,
    is_preview: bool = False,
):
    """Export view for LOM records."""
    exporter = current_app.config.get("LOM_RECORD_EXPORTERS", {}).get(export_format)
    if exporter is None:
        abort(404)

    serializer = obj_or_import_string(exporter["serializer"])(
        options={
            "indent": 2,
            "sort_keys": True,
        }
    )
    exported_record = serializer.serialize_object(record.to_dict())
    return render_template(
        "invenio_records_lom/records/export.html",
        export_format=exporter.get("name", export_format),
        exported_record=exported_record,
        record=LOMUIJSONSerializer().serialize_object_to_dict(record.to_dict()),
        permissions=record.has_permissions_to(["update_draft"]),
        is_preview=is_preview,
        is_draft=record._record.is_draft,
    )


@pass_is_preview
@pass_record_or_draft
@pass_file_metadata
def record_file_preview(
    record: RecordItem = None,
    pid_value: str = None,
    pid_type: str = "recid",
    file_metadata: FileItem = None,
    is_preview: bool = False,
    **kwargs,
):
    """Render a preview of the specified file."""
    file_previewer = file_metadata.data.get("previewer")
    url = url_for(
        "invenio_records_lom.record_file_download",
        pid_value=pid_value,
        filename=file_metadata.data["key"],
        preview=1 if is_preview else 0,
    )

    # find a suitable previewer
    file_obj = PreviewFile(file_metadata, pid_value, url)
    for plugin in current_previewer.iter_previewers(
        previewers=[file_previewer] if file_previewer else None
    ):
        if plugin.can_preview(file_obj):
            return plugin.preview(file_obj)

    return default.preview(file_obj)


@pass_is_preview
@pass_file_item
def record_file_download(
    file_item: FileItem = None,
    pid_value: str = None,
    is_preview: bool = False,
    **kwargs,
):
    """Download a file from a record."""
    download = bool(request.args.get("download"))
    return file_item.send_file(as_attachment=download)


@pass_record_latest
def record_latest(record: RecordItem = None, **kwargs):
    """Redirect to record's landing page."""
    return redirect(record["links"]["self_html"], code=301)


@pass_record_from_pid
def record_from_pid(record: RecordItem = None, **kwargs):
    """Redirect to record's landing page."""
    return redirect(record["links"]["self_html"], code=301)
