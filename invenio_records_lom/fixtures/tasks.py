# SPDX-FileCopyrightText: 2023-2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Fake LOM demo records via task."""

from celery import shared_task
from flask_principal import Identity
from invenio_access.permissions import any_user, authenticated_user, system_process
from invenio_records_resources.services.records.results import RecordItem

from ..proxies import current_records_lom


def system_identity() -> Identity:
    """System identity."""
    identity = Identity(3)
    identity.provides.add(any_user)
    identity.provides.add(authenticated_user)
    identity.provides.add(system_process)
    return identity


@shared_task(ignore_result=True)
def create_lom_record(data: dict) -> RecordItem:
    """Create records for demo purposes."""
    service = current_records_lom.records_service
    draft = service.create(
        data=data,
        identity=system_identity(),
    )
    return service.publish(id_=draft.id, identity=system_identity())
