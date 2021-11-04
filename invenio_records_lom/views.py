# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Blueprint definitions."""

from __future__ import absolute_import, print_function

from functools import wraps

from flask import Blueprint, g, render_template, request

from sqlalchemy.orm.exc import NoResultFound

from .proxies import current_records_lom
from .resources.serializers import LOMUIJSONSerializer


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


@pass_is_preview
@pass_record_or_draft
# @pass_record_files
def record_detail(pid_value=None, is_preview=None, record=None, files=None):
    files_dict = {} if files is None else files.to_dict()

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


def create_blueprint(app):
    routes = app.config["LOM_ROUTES"]

    blueprint = Blueprint(
        "invenio_records_lom",
        __name__,
        template_folder="templates",
        static_folder="static",
    )

    blueprint.add_url_rule(
        routes["record_detail"],
        view_func=record_detail,
    )

    return blueprint
