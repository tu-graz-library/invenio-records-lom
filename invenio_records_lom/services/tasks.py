# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Celery tasks for LOM module."""

from celery import shared_task
from invenio_access.permissions import system_identity

from ..proxies import current_records_lom


@shared_task(ignore_result=True)
def register_or_update_pid(recid: str, scheme: str):
    """Update PID on remote providers."""
    current_records_lom.records_service.pids.register_or_update(
        id_=recid,
        identity=system_identity,
        scheme=scheme,
    )
