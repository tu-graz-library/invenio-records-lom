# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""PIDsService tests."""

import pytest
from invenio_pidstore.errors import PIDDoesNotExistError
from invenio_pidstore.models import PIDStatus

from invenio_records_lom.resources.serializers import LOMToDataCite44Serializer
from invenio_records_lom.services.tasks import register_or_update_pid


def test_resolve_pid(service, db, identity, full_lom_metadata):
    """Resolve a PID."""
    draft = service.create(identity=identity, data=full_lom_metadata)
    record = service.publish(identity=identity, id_=draft.id)
    doi = record["pids"]["doi"]["identifier"]

    resolved_record = service.pids.resolve(identity=identity, id_=doi, scheme="doi")

    assert resolved_record.id == record.id
    assert resolved_record["pids"]["doi"]["identifier"] == doi


def test_resolve_nonexisting_pid(service, identity):
    """Attempt to resolve a non-existing pid."""
    fake_doi = "10,4321/client.12345-invalid"

    with pytest.raises(PIDDoesNotExistError):
        service.pids.resolve(identity=identity, id_=fake_doi, scheme="doi")


def test_reserve_pid(service, db, identity, full_lom_metadata):
    """Reserve a new pid."""
    draft = service.create(identity=identity, data=full_lom_metadata)
    draft = service.pids.create(identity=identity, id_=draft.id, scheme="doi")
    doi = draft["pids"]["doi"]["identifier"]

    provider = service.pids.pid_manager._get_provider("doi", "datacite")
    pid = provider.get(pid_value=doi)

    assert pid.status == PIDStatus.NEW


def test_datacite_schema(service, db, full_lom_metadata):
    """Dump a LOM-object with LOMSerializer."""
    datacite_data = LOMToDataCite44Serializer().dump_one(full_lom_metadata)
    mandatory_keys = [
        "publicationYear",
        "creators",
        "titles",
        "identifiers",
        "types",
        "publisher",
    ]
    assert all(key in datacite_data for key in mandatory_keys)


def test_register_pid(service, db, identity, full_lom_metadata, mocker):
    """Register a pid."""

    def public_doi(self, metadata, url, doi):
        """Mock doi publication."""
        pass

    mocker.patch(
        "invenio_rdm_records.services.pids.providers.datacite.DataCiteRESTClient.public_doi",
        public_doi,
    )

    draft = service.create(identity=identity, data=full_lom_metadata)
    draft = service.pids.create(identity=identity, id_=draft.id, scheme="doi")
    doi = draft["pids"]["doi"]["identifier"]

    provider = service.pids.pid_manager._get_provider("doi", "datacite")
    pid = provider.get(pid_value=doi)

    record = service.record_cls.publish(draft._record)
    record.pids = {
        pid.pid_type: {
            "identifier": pid.pid_value,
            "provider": "datacite",
        }
    }
    record.metadata = draft["metadata"]
    record.register()
    record.commit()
    assert pid.status == PIDStatus.NEW
    pid.reserve()
    assert pid.status == PIDStatus.RESERVED
    register_or_update_pid(recid=record["id"], scheme="doi")
    assert pid.status == PIDStatus.REGISTERED
