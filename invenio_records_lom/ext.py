# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Flask extension for invenio-records-lom."""

from __future__ import absolute_import, print_function

from invenio_records_resources.services import FileService
from werkzeug.utils import cached_property

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

    @cached_property
    def lom_cls(self):
        """Base Lom API class."""
        # TODO: Refactor
        # def default_class_factory():
        #     from .api import LomRecordBase
        #     return type(
        #         'InvenioRecordsLOM',
        #         (LomRecordBase),
        #         {},
        #     )
        # return self.app.config['LOM_CLS'] or default_class_factory()

        from .api import LomRecordBase

        return type(
            "Lom",
            (LomRecordBase,),
            {},
        )

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
                if k == "LOM_REST_ENDPOINTS":
                    # Make sure of registration process.
                    app.config.setdefault("RECORDS_REST_ENDPOINTS", {})
                    app.config["RECORDS_REST_ENDPOINTS"].update(getattr(config, k))

                if k == "LOM_REST_FACETS":
                    app.config.setdefault("RECORDS_REST_FACETS", {})
                    app.config["RECORDS_REST_FACETS"].update(getattr(config, k))

                app.config.setdefault(k, getattr(config, k))
                if k == "LOM_REST_SORT_OPTIONS":
                    # TODO Might be overriden depending on which package is
                    # initialised first
                    app.config.setdefault("RECORDS_REST_SORT_OPTIONS", {})
                    app.config["RECORDS_REST_SORT_OPTIONS"].update(getattr(config, k))
                if k == "LOM_REST_DEFAULT_SORT":
                    # TODO Might be overriden depending on which package is
                    # initialised first
                    app.config.setdefault("RECORDS_REST_DEFAULT_SORT", {})
                    app.config["RECORDS_REST_DEFAULT_SORT"].update(getattr(config, k))

    def init_services(self, app):
        """Initialize Services."""
        service_config = (
            LOMRecordServiceConfig  # config_class as in invenio-RDM and invenio-MARC21
        )

        self.records_service = LOMRecordService(
            service_config,
            files_service=FileService(LOMRecordFilesServiceConfig),
            draft_files_service=FileService(LOMDraftFilesServiceConfig),
        )

    def init_resources(self, app):
        self.records_resource = LOMRecordResource(
            LOMRecordResourceConfig,
            self.records_service,
        )
