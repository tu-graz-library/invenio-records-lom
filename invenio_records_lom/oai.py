# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""OAI-PMH serializers for LOM-records."""

from flask import current_app, g
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_pidstore.models import PersistentIdentifier
from invenio_records_resources.services.errors import PermissionDeniedError

from .proxies import current_records_lom
from .resources.serializers import LOMToLOMXMLSerializer


def lom_etree(pid, record):
    """Get LOM XML for OAI-PMH."""
    return LOMToLOMXMLSerializer(
        metadata=record["_source"]["metadata"],
        lom_id=record["_source"]["id"],
        oaiserver_id_prefix=current_app.config.get("OAISERVER_ID_PREFIX"),
    ).serialize_object_xml()


def getrecord_fetcher(record_id):
    """Fetch record data as dict with identity check for serialization."""
    lomid = PersistentIdentifier.get_by_object(
        pid_type="lomid", object_uuid=record_id, object_type="rec"
    )

    try:
        result = current_records_lom.records_service.read(g.identity, lomid.pid_value)
    except PermissionDeniedError:
        # if it is a restricted record.
        raise PIDDoesNotExistError("lomid", None)

    return result.to_dict()
