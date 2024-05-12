# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""OAI-PMH serializers for LOM-records."""

from flask import current_app, g
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_pidstore.models import PersistentIdentifier
from invenio_records_resources.services.errors import PermissionDeniedError
from invenio_records_resources.services.result import RecordItem

from .proxies import current_records_lom
from .resources.serializers import LOMToOAIXMLSerializer


def lom_etree(
    pid: str,  # noqa: ARG001
    record: dict,
) -> dict:
    """Get LOM XML for OAI-PMH."""
    try:
        # the doi creation is optional and depends on the variable
        # DATACITE_ENABLED
        doi = record["_source"]["pids"]["doi"]["identifier"]
    except KeyError:
        doi = None

    return LOMToOAIXMLSerializer(
        metadata=record["_source"]["metadata"],
        lom_id=record["_source"]["id"],
        oaiserver_id_prefix=current_app.config.get("OAISERVER_ID_PREFIX"),
        doi=doi,
    ).dump_obj()


def getrecord_fetcher(record_id: str) -> dict:
    """Fetch record data as dict with identity check for serialization."""
    lomid = PersistentIdentifier.get_by_object(
        pid_type="lomid",
        object_uuid=record_id,
        object_type="rec",
    )

    try:
        result = current_records_lom.records_service.read(g.identity, lomid.pid_value)
    except PermissionDeniedError as error:
        # if it is a restricted record.
        msg = "lomid"
        raise PIDDoesNotExistError(msg, None) from error

    return result.to_dict()


def getrecord_sets_fetcher(_: RecordItem) -> list:
    """Fetch sets of the record."""
    return []
