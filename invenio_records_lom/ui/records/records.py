from os.path import splitext

from flask import render_template, url_for

from ...resources.serializers import LOMUIJSONSerializer
from .decorators import pass_is_preview, pass_record_files, pass_record_or_draft


class PreviewFile:
    """Preview file implementation for InvenioRDM.

    This class was apparently created because of subtle differences with
    `invenio_previewer.api.PreviewFile`.
    """

    def __init__(self, file_item, record_pid_value, url=None):
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
def record_detail(pid_value=None, is_preview=None, record=None, files=None):
    files_dict = {} if files is None else files.to_dict()

    # TODO: marc21 and app-rdm go differently about this, chose one
    # cf. UIJSONSerializer().serialize_object_to_dict(record.to_dict())
    serializer = LOMUIJSONSerializer()
    dict_record = record.to_dict()
    from copy import deepcopy

    ser_obj = deepcopy(dict_record)
    schema = serializer.object_schema_cls()
    dump = schema.dump(ser_obj)
    ser_obj["ui"] = dump
    ser_obj["pids"] = {}

    return render_template(
        "invenio_records_lom/record.html",
        record=ser_obj,
        pid=pid_value,
        files=files_dict,
        permissions=record.has_permissions_to(
            ["edit", "new_version", "manage", "update_draft", "read_files"]
        ),
        is_preview=is_preview,
        is_draft=record._record.is_draft,
    )


# TODO
def record_export(*a, **k):
    return "<p>not implemented</p>"


# TODO
def record_file_preview(*a, **k):
    return "<p>not implemented</p>"


# TODO
def record_file_download(*a, **k):
    return "<p>not implemented</p>"
