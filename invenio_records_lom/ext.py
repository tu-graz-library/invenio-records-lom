# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Flask extension for invenio-records-lom."""
from invenio_rdm_records.services.pids import PIDManager, PIDsService
from invenio_records_resources.resources import FileResource
from invenio_records_resources.services import FileService

from . import config
from .resources import (
    LOMDraftFilesResourceConfig,
    LOMRecordFilesResourceConfig,
    LOMRecordResource,
    LOMRecordResourceConfig,
)
from .services import (
    LOMDraftFilesServiceConfig,
    LOMRecordFilesServiceConfig,
    LOMRecordService,
    LOMRecordServiceConfig,
)


class InvenioRecordsLOM:
    """invenio-records-lom extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask application initialization."""
        self.init_config(app)
        self.init_services(app)
        self.init_resources(app)
        app.extensions["invenio-records-lom"] = self

    def init_config(self, app):
        """Initialize configuration.

        Override configuration variables with the values in this package.
        """
        for k in dir(config):
            if k == "LOM_PERSISTENT_IDENTIFIER_PROVIDERS":
                app.config.setdefault("LOM_PERSISTENT_IDENTIFIER_PROVIDERS", [])
                app.config["LOM_PERSISTENT_IDENTIFIER_PROVIDERS"].extend(
                    getattr(config, k)
                )

            elif k == "LOM_PERSISTENT_IDENTIFIERS":
                app.config.setdefault("LOM_PERSISTENT_IDENTIFIERS", {})
                app.config["LOM_PERSISTENT_IDENTIFIERS"].update(getattr(config, k))

            if k.startswith("LOM_"):
                app.config.setdefault(k, getattr(config, k))

    def init_services(self, app):
        """Initialize services."""
        record_service_config = LOMRecordServiceConfig.build(app)
        files_service_config = LOMRecordFilesServiceConfig.build(app)
        draft_files_config = LOMDraftFilesServiceConfig.build(app)
        # pylint: disable-next=attribute-defined-outside-init
        self.records_service = LOMRecordService(
            config=record_service_config,
            files_service=FileService(files_service_config),
            draft_files_service=FileService(draft_files_config),
            pids_service=PIDsService(record_service_config, PIDManager),
        )

    def init_resources(self, app):  # pylint: disable=unused-argument
        """Initialize resouces."""
        # pylint: disable-next=attribute-defined-outside-init
        self.draft_files_resource = FileResource(
            config=LOMDraftFilesResourceConfig,
            service=self.records_service.draft_files,
        )

        # pylint: disable-next=attribute-defined-outside-init
        self.record_files_resource = FileResource(
            config=LOMRecordFilesResourceConfig,
            service=self.records_service.files,
        )

        # pylint: disable-next=attribute-defined-outside-init
        self.records_resource = LOMRecordResource(
            config=LOMRecordResourceConfig,
            service=self.records_service,
        )
