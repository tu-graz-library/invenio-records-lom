# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2022 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Config classes for LOMRecordService-objects."""

from invenio_drafts_resources.services.records.components import (
    DraftFilesComponent,
    PIDComponent,
    RelationsComponent,
)
from invenio_drafts_resources.services.records.config import (
    RecordServiceConfig,
    is_draft,
    is_record,
)
from invenio_rdm_records.services.components import AccessComponent, MetadataComponent
from invenio_rdm_records.services.config import has_doi, is_record_and_has_doi
from invenio_records_resources.services import (
    ConditionalLink,
    FileLink,
    FileServiceConfig,
    Link,
    RecordLink,
)
from invenio_records_resources.services.base.config import ConfiguratorMixin

from ..records import LOMDraft, LOMRecord
from .components import LOMPIDsComponent, ResourceTypeComponent
from .permissions import LOMRecordPermissionPolicy
from .schemas import LOMRecordSchema


class FromConfigLOMPIDsProviders:
    """Data descriptor for pid providers configuration."""

    def __get__(self, obj, objtype=None):
        """Return dictionary keyed by scheme, with {"name1": provider1, ...} as values."""
        configs_by_scheme = obj._app.config.get("LOM_PERSISTENT_IDENTIFIERS", {})
        providers = obj._app.config.get("LOM_PERSISTENT_IDENTIFIER_PROVIDERS", [])
        doi_enabled = obj._app.config.get("DATACITE_ENABLED", False)

        providers_by_name = {p.name: p for p in providers}

        providerdicts_by_scheme = {}
        for scheme, config in configs_by_scheme.items():
            if scheme == "doi" and not doi_enabled:
                continue

            providerdict = {"default": None}
            for name in config.get("providers", []):
                # This may throw a KeyError which usually signifies an incorrect config
                providerdict[name] = providers_by_name[name]
                providerdict["default"] = providerdict["default"] or name

            providerdicts_by_scheme[scheme] = providerdict
        return providerdicts_by_scheme


class FromConfigLOMRequiredPIDs:
    """Data descriptor for required pids configuration."""

    def __get__(self, obj, objtype=None):
        """Return list of enabled required schemes."""
        configs_by_scheme = obj._app.config.get("LOM_PERSISTENT_IDENTIFIERS", {})
        doi_enabled = obj._app.config.get("DATACITE_ENABLED", False)

        enabled_schemes = (
            scheme for scheme in configs_by_scheme if scheme != "doi" or doi_enabled
        )

        return [
            scheme
            for scheme in enabled_schemes
            if configs_by_scheme[scheme].get("required", False)
        ]


class LOMRecordServiceConfig(RecordServiceConfig, ConfiguratorMixin):
    """Config for LOM record service."""

    # Record and draft class
    draft_cls = LOMDraft
    record_cls = LOMRecord

    # Schemas
    schema = LOMRecordSchema

    permission_policy_cls = LOMRecordPermissionPolicy

    # PIDConfiguration
    pids_providers = FromConfigLOMPIDsProviders()
    pids_required = FromConfigLOMRequiredPIDs()

    # links
    links_item = {
        "doi": Link(
            "https://doi.org/{+pid_doi}",
            when=has_doi,
            vars=lambda record, vars: vars.update(
                {
                    f"pid_{scheme}": pid["identifier"]
                    for (scheme, pid) in record.pids.items()
                }
            ),
        ),
        "files": ConditionalLink(
            cond=is_record,
            if_=RecordLink("{+api}/lom/{id}/files"),
            else_=RecordLink("{+api}/lom/{id}/draft/files"),
        ),
        "latest_html": RecordLink("{+ui}/lom/id/latest", when=is_record),
        "publish": RecordLink("{+api}/lom/{id}/draft/actions/publish", when=is_draft),
        "record_html": RecordLink("{+ui}/lom/{id}", when=is_draft),
        "reserve_doi": RecordLink("{+api}/lom/{id}/draft/pids/doi"),
        "self": ConditionalLink(
            cond=is_record,
            if_=RecordLink("{+api}/lom/{id}"),
            else_=RecordLink("{+api}/lom/{id}/draft"),
        ),
        "self_doi": Link(
            "{+ui}/lom/doi/{+pid_doi}",
            when=is_record_and_has_doi,
            vars=lambda record, vars: vars.update(
                {
                    f"pid_{scheme}": pid["identifier"]
                    for (scheme, pid) in record.pids.items()
                }
            ),
        ),
        "self_html": ConditionalLink(
            cond=is_record,
            if_=RecordLink("{+ui}/lom/{id}"),
            else_=RecordLink("{+ui}/lom/uploads/{id}"),
        ),
    }

    components = [
        MetadataComponent,
        AccessComponent,
        DraftFilesComponent,
        PIDComponent,
        LOMPIDsComponent,
        RelationsComponent,
        ResourceTypeComponent,
    ]


class LOMDraftFilesServiceConfig(FileServiceConfig, ConfiguratorMixin):
    """Config for LOM draft files service."""

    record_cls = LOMDraft
    permission_action_prefix = "draft_"
    permission_policy_cls = LOMRecordPermissionPolicy

    # links to appear within FileList-result:
    file_links_list = {
        "self": RecordLink("{+api}/lom/{id}/draft/files"),
    }

    # links to appear within the items of FileList-results:
    # (note that, due to `Link.should_render`, some of these links may not appear on items)
    file_links_item = {
        "commit": FileLink("{+api}/lom/{id}/draft/files/{key}/commit"),
        "content": FileLink("{+api}/lom/{id}/draft/files/{key}/content"),
        "self": FileLink("{+api}/lom/{id}/draft/files/{key}"),
    }


class LOMRecordFilesServiceConfig(FileServiceConfig, ConfiguratorMixin):
    """Config for LOM files service."""

    record_cls = LOMRecord
    permission_policy_cls = LOMRecordPermissionPolicy

    file_links_list = {}
    file_links_item = {}
