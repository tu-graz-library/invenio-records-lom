# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Flask extension for invenio-records-lom."""
from invenio_rdm_records.services.pids import PIDManager, PIDsService
from invenio_records_resources.services import FileService

from . import config
from .resources import LOMRecordResource, LOMRecordResourceConfig
from .services import (
    LOMDraftFilesServiceConfig,
    LOMRecordFilesServiceConfig,
    LOMRecordService,
    LOMRecordServiceConfig,
)


class InvenioRecordsLOM(object):
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
            if k.startswith("LOM_"):
                app.config.setdefault(k, getattr(config, k))

    def init_services(self, app):
        """Initialize services."""
        record_service_config = LOMRecordServiceConfig.build(app)
        file_service_config = LOMRecordFilesServiceConfig.build(app)
        draft_files_config = LOMDraftFilesServiceConfig.build(app)

        self.records_service = LOMRecordService(
            config=record_service_config,
            files_service=FileService(file_service_config),
            draft_files_service=FileService(draft_files_config),
            pids_service=PIDsService(record_service_config, PIDManager),
        )

    def init_resources(self, app):
        """Initialize resouces."""
        self.records_resource = LOMRecordResource(
            LOMRecordResourceConfig,
            self.records_service,
        )
