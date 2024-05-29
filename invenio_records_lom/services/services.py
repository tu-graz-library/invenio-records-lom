# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2024 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Record services configured for LOM-use."""

from invenio_rdm_records.services import RDMRecordService
from invenio_records_resources.services.uow import unit_of_work

from ..utils import LOMMetadata


# pylint: disable-next=abstract-method
class LOMRecordService(RDMRecordService):
    """RecordService configured for LOM-use."""

    @unit_of_work()
    def create(self, identity, data, uow=None, expand=False):
        """Create."""
        print(f"LOMRecordService.create data: {data}")
        draft_item = super().create(identity, data, uow=uow, expand=expand)

        # # add repo-pid to the record's identifiers
        # metadata = LOMMetadata(data["metadata"])
        # metadata.append_identifier(draft_item.id, catalog="repo-pid")
        # data["metadata"] = metadata.json

        print(
            f"LOMRecordService.create id: {draft_item.id}, draft_item: {draft_item._record}"
        )
        return draft_item
        # return super().update_draft(
        #     identity=identity,
        #     id_=draft_item.id,
        #     data=data,
        #     uow=uow,
        #     expand=expand,
        # )
