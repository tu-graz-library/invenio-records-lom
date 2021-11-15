from functools import wraps

from flask import g, request
from invenio_records_resources.services.errors import PermissionDeniedError
from sqlalchemy.orm.exc import NoResultFound

from ...proxies import current_records_lom


def pass_is_preview(func):
    @wraps(func)
    def decoed(**kwargs):
        is_preview = request.args.get("preview") == "1"
        return func(**kwargs, is_preview=is_preview)

    return decoed


def pass_record_or_draft(func):
    @wraps(func)
    def decoed(**kwargs):
        is_preview = kwargs.get("is_preview", False)
        service = current_records_lom.records_service
        service_kwargs = {"id_": kwargs.get("pid_value"), "identity": g.identity}

        if is_preview:
            try:
                record_item = service.read_draft(**service_kwargs)
            except NoResultFound:
                record_item = service.read(**service_kwargs)
        else:
            record_item = service.read(**service_kwargs)

        return func(**kwargs, record=record_item)

    return decoed


def pass_record_files(func):
    @wraps(func)
    def decoed(**kwargs):
        is_preview = kwargs.get("is_preview", False)
        draft_files_service = current_records_lom.records_service.draft_files
        files_service = current_records_lom.records_service.files
        service_kwargs = {"id_": kwargs.get("pid_value"), "identity": g.identity}

        try:
            if is_preview:
                try:
                    files = draft_files_service.list_files(**service_kwargs)
                except NoResultFound:
                    files = files_service.list_files(**service_kwargs)
            else:
                files = files_service.list_files(**service_kwargs)

        except PermissionDeniedError:
            files = None

        return func(**kwargs, files=files)

    return decoed


def pass_file_metadata(func):
    @wraps(func)
    def decoed(**kwargs):
        is_preview = kwargs.get("is_preview", False)
        draft_files_service = current_records_lom.records_service.draft_files
        files_service = current_records_lom.records_service.files
        service_kwargs = {
            "id_": kwargs.get("pid_value"),
            "file_key": kwargs.get("filename"),
            "identity": g.identity,
        }

        if is_preview:
            try:
                file_metadata = draft_files_service.read_file_metadata(**service_kwargs)
            except NoResultFound:
                file_metadata = files_service.read_file_metadata(**service_kwargs)
        else:
            file_metadata = files_service.read_file_metadata(**service_kwargs)

        return func(**kwargs, file_metadata=file_metadata)

    return decoed


def pass_file_item(func):
    @wraps(func)
    def decoed(**kwargs):
        is_preview = kwargs.get("is_preview", False)
        draft_files_service = current_records_lom.records_service.draft_files
        files_service = current_records_lom.records_service.files
        service_kwargs = {
            "id_": kwargs.get("pid_value"),
            "file_key": kwargs.get("filename"),
            "identity": g.identity,
        }

        if is_preview:
            try:
                file_item = draft_files_service.get_file_content(**service_kwargs)
            except NoResultFound:
                file_item = files_service.get_file_content(**service_kwargs)
        else:
            file_item = files_service.get_file_content(**service_kwargs)

        return func(**kwargs, file_item=file_item)

    return decoed
