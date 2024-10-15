# -*- coding: utf-8 -*-
#
# Copyright (C) 2019-2021 CERN.
# Copyright (C) 2019-2021 Northwestern University.
# Copyright (C)      2021 TU Wien.
# Copyright (C) 2021-2024 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
# For the original code see the NOTE below.


# NOTE:
# copy-pasted code from invenio_app_rdm/records_ui/views/decorators.py
# copy-pasting was necessary to overrride the standard-behavior with custom behavior

"""View-functions for record-related pages."""

from pathlib import Path

from flask import abort, current_app, g, redirect, render_template, request, url_for
from invenio_base.utils import obj_or_import_string
from invenio_previewer.extensions import default
from invenio_previewer.proxies import current_previewer
from invenio_records_resources.services.files.results import FileItem, FileList
from invenio_records_resources.services.records.results import RecordItem
from invenio_stats.proxies import current_stats
from marshmallow import ValidationError

from ...proxies import current_records_lom
from ...resources.serializers import LOMToUIJSONSerializer
from .decorators import (
    pass_file_item,
    pass_file_metadata,
    pass_include_deleted,
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

    def __init__(
        self,
        file_item: FileItem,
        record_pid_value: str,
        url: str | None = None,
    ) -> None:
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

    def is_local(self) -> bool:
        """Check if file is local."""
        return True

    def has_extensions(self, *exts: dict) -> bool:
        """Check if file has one of the extensions.

        Each `exts` has the format `.{file type}` e.g. `.txt` .
        """
        file_ext = Path(self.data["key"]).suffix.lower()
        return file_ext in exts

    def open(self):  # noqa:ANN201
        """Open the file."""
        return self.file._file.file.storage().open()  # noqa: SLF001


#
# Views
#
@pass_is_preview
@pass_include_deleted
@pass_record_or_draft
@pass_record_files
def record_detail(
    pid_value: str | None = None,
    is_preview: bool | None = None,
    record: RecordItem = None,
    files: FileList | None = None,
    *,
    include_deleted: bool = False,
) -> str:
    """Record detail page (aka landing page)."""
    files_dict = {} if files is None else files.to_dict()
    record_ui = LOMToUIJSONSerializer().dump_obj(record.to_dict())

    is_draft = record_ui["is_draft"]
    if is_preview and is_draft:
        try:
            current_records_lom.records_service.validate_draft(g.identity, record.id)
        except ValidationError:
            abort(404)

    # emit a record view stats event
    emitter = current_stats.get_event_emitter("lom-record-view")
    if record is not None and emitter is not None:
        emitter(current_app, record=record._record, via_api=False)  # noqa: SLF001

    return render_template(
        "invenio_records_lom/record.html",
        files=files_dict,
        include_deleted=include_deleted,
        is_draft=is_draft,
        is_preview=is_preview,
        permissions=record.has_permissions_to(
            ["edit", "new_version", "manage", "update_draft", "read_files", "review"],
        ),
        pid=pid_value,
        record=record_ui,
    )


@pass_is_preview
@pass_record_or_draft
def record_export(
    record: RecordItem = None,
    export_format: str | None = None,
    pid_value: str | None = None,
    *,
    is_preview: bool | None = False,  # noqa: ARG001
) -> tuple[dict, int, dict]:
    """Export view for LOM records."""
    exporter = current_app.config.get("LOM_RECORD_EXPORTERS", {}).get(export_format)
    if exporter is None:
        abort(404)

    serializer = obj_or_import_string(exporter["serializer"])(
        options={
            "indent": 2,
            "sort_keys": True,
        },
    )
    exported_record = serializer.serialize_object(record.to_dict())
    content_type = exporter.get("content-type", export_format)
    filename = exporter.get("filename", export_format).format(id=pid_value)
    headers = {
        "Content-Type": content_type,
        "Content-Disposition": f"attachment; filename={filename}",
    }
    return (exported_record, 200, headers)


@pass_is_preview
@pass_record_or_draft
@pass_file_metadata
def record_file_preview(  # noqa: ANN201
    pid_value: str | None = None,
    record: RecordItem | None = None,  # noqa: ARG001
    pid_type: str = "recid",  # noqa: ARG001
    file_metadata: FileItem | None = None,
    *,
    is_preview: bool | None = False,
    include_deleted: bool | None = False,  # noqa: ARG001
    **__,  # noqa: ANN003
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
    previewers = [file_previewer] if file_previewer else None
    for plugin in current_previewer.iter_previewers(previewers=previewers):
        if plugin.can_preview(file_obj):
            return plugin.preview(file_obj)

    return default.preview(file_obj)


@pass_is_preview
@pass_file_item
def record_file_download(  # noqa: ANN201
    file_item: FileItem = None,
    pid_value: str | None = None,  # noqa: ARG001
    *,
    is_preview: bool = False,  # noqa: ARG001
):
    """Download a file from a record."""
    # emit a file download stats event
    emitter = current_stats.get_event_emitter("lom-file-download")
    if file_item is not None and emitter is not None:
        # pylint: disable-next=protected-access
        obj = file_item._file.object_version  # noqa: SLF001
        # pylint: disable-next=protected-access
        emitter(
            current_app,
            record=file_item._record,  # noqa: SLF001
            obj=obj,
            via_api=False,
        )

    download = bool(request.args.get("download"))
    return file_item.send_file(as_attachment=download)


@pass_record_latest
def record_latest(  # noqa: ANN201
    record: RecordItem = None,
):
    """Redirect to record's landing page."""
    return redirect(record["links"]["self_html"], code=301)


@pass_record_from_pid
def record_from_pid(  # noqa: ANN201
    record: RecordItem = None,
):
    """Redirect to record's landing page."""
    return redirect(record["links"]["self_html"], code=301)
