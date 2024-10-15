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
# copy-pasting was necessary to overrride the standard-service with this module's
# service


"""Decorates for record-view-functions."""

from collections.abc import Callable
from functools import wraps

from flask import g, redirect, request, url_for
from invenio_records_resources.services.errors import PermissionDeniedError
from sqlalchemy.orm.exc import NoResultFound

from ...proxies import current_records_lom


def pass_include_deleted[T](func: Callable[..., T]) -> Callable:
    """Retrive `include_deleted` from request-args and pass into decorated function."""

    @wraps(func)
    def decoed(**kwargs: dict) -> T:
        include_deleted = request.args.get("include_deleted") == "1"
        return func(**kwargs, include_deleted=include_deleted)

    return decoed


def pass_is_oer_certified[T](func: Callable[..., T]) -> Callable:
    """Check if the logged in user has the permission to create oer's."""

    @wraps(func)
    def decoed(**kwargs: dict) -> T:
        service = current_records_lom.records_service
        is_oer_certified = service.check_permission(g.identity, "handle_oer")
        return func(**kwargs, is_oer_certified=is_oer_certified)

    return decoed


def pass_record_latest[T](func: Callable[..., T]) -> Callable:
    """Retrieve latest version of `record` from db and pass into decorated function."""

    @wraps(func)
    def decoed(**kwargs: dict) -> T:
        service = current_records_lom.records_service
        record_latest = service.read_latest(
            identity=g.identity,
            id_=kwargs.get("pid_value"),
        )
        return func(**kwargs, record=record_latest)

    return decoed


def pass_record_from_pid[T](func: Callable[..., T]) -> Callable:
    """Retrieve `record` via passed-in pid-info and pass into decorated function."""

    @wraps(func)
    def decoed(**kwargs: dict) -> T:
        service = current_records_lom.records_service
        record = service.pids.resolve(
            identity=g.identity,
            id_=kwargs.get("pid_value"),
            scheme=kwargs.get("pid_scheme"),
        )
        return func(**kwargs, record=record)

    return decoed


def pass_is_preview[T](func: Callable[..., T]) -> Callable:
    """Retrieve `is_preview` from request and pass that into decorated function."""

    @wraps(func)
    def decoed(**kwargs: dict) -> T:
        is_preview = request.args.get("preview") == "1"
        return func(**kwargs, is_preview=is_preview)

    return decoed


def pass_record_or_draft[T](func: Callable[..., T]) -> Callable:
    """Retrieve `record` from database and pass that into decorated function."""

    @wraps(func)
    def decoed(**kwargs: dict) -> T:
        is_preview = kwargs.get("is_preview", False)
        service = current_records_lom.records_service
        service_kwargs = {"identity": g.identity, "id_": kwargs.get("pid_value")}

        if is_preview:
            try:
                record_item = service.read_draft(**service_kwargs)
            except NoResultFound:
                record_item = service.read(**service_kwargs)
        else:
            record_item = service.read(**service_kwargs)

        return func(**kwargs, record=record_item)

    return decoed


def pass_record_files[T](func: Callable[..., T]) -> Callable:
    """Retrieve `files` from database and pass that into decorated function."""

    @wraps(func)
    def decoed(**kwargs: dict) -> T:
        is_preview = kwargs.get("is_preview", False)
        draft_files_service = current_records_lom.records_service.draft_files
        files_service = current_records_lom.records_service.files
        service_kwargs = {"identity": g.identity, "id_": kwargs.get("pid_value")}

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


def pass_file_metadata[T](func: Callable[..., T]) -> Callable:
    """Retrieve `file_metadata` from database and pass that into decorated function."""

    @wraps(func)
    def decoed(**kwargs: dict) -> T:
        is_preview = kwargs.get("is_preview", False)
        draft_files_service = current_records_lom.records_service.draft_files
        files_service = current_records_lom.records_service.files
        service_kwargs = {
            "identity": g.identity,
            "id_": kwargs.get("pid_value"),
            "file_key": kwargs.get("filename"),
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


def pass_file_item[T](func: Callable[..., T]) -> Callable:
    """Retrieve `file_item` from database and pass that into decorated function."""

    @wraps(func)
    def decoed(**kwargs: dict) -> T:
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


def pass_draft(*, expand: bool = False) -> Callable:
    """Retrieve `draft` via passed-in `pid_value` and pass into decorated function."""

    def decorator[T](func: Callable[..., T]) -> Callable:
        @wraps(func)
        def decoed(**kwargs: dict) -> T:
            service = current_records_lom.records_service
            draft = service.read_draft(
                identity=g.identity,
                id_=kwargs.get("pid_value"),
                expand=expand,
            )
            return func(**kwargs, draft=draft)

        return decoed

    return decorator


def pass_draft_files[T](func: Callable[..., T]) -> Callable:
    """Retrieve `draft_files` from database and pass that into decorated function."""

    @wraps(func)
    def decoed(**kwargs: dict) -> T:
        draft_files_service = current_records_lom.records_service.draft_files
        try:
            draft_files = draft_files_service.list_files(
                identity=g.identity,
                id_=kwargs.get("pid_value"),
            )
        except PermissionDeniedError:
            draft_files = None

        return func(**kwargs, draft_files=draft_files)

    return decoed


def require_lom_permission(action_name: str, *, default_endpoint: str) -> Callable:
    """Require permission from permission-policy or redirect to `default_endpoint`.

    example usage:
    @require_lom_permission('create', 'invenio_records_lom.uploads')
    checks `flask.g.identity` against `LOMPermissionPolicy.can_create`
    if no permission redirects to endpoint "uploads" of blueprint "invenio_records_lom"
    """

    def view_decorator[T](view_func: Callable[..., T]) -> Callable:
        @wraps(view_func)
        def decorated_view(*args: dict, **kwargs: dict) -> T:
            service = current_records_lom.records_service
            if not service.check_permission(g.identity, action_name):
                return redirect(url_for(default_endpoint))
            return view_func(*args, **kwargs)

        return decorated_view

    return view_decorator
