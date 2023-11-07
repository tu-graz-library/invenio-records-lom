# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2023 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Config classes for LOMRecordService-objects."""

from invenio_drafts_resources.services.records.config import (
    RecordServiceConfig,
    SearchDraftsOptions,
    SearchOptions,
    is_draft,
    is_record,
)
from invenio_rdm_records.services.config import (
    has_doi,
    is_iiif_compatible,
    is_record_and_has_doi,
)
from invenio_records_resources.services import (
    ConditionalLink,
    FileLink,
    FileServiceConfig,
    Link,
    RecordLink,
    pagination_links,
)
from invenio_records_resources.services.base.config import (
    ConfiguratorMixin,
    FromConfig,
    FromConfigSearchOptions,
    SearchOptionsMixin,
)

from ..records import LOMDraft, LOMRecord
from . import facets
from .components import DefaultRecordsComponents
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


class LOMSearchOptions(SearchOptions, SearchOptionsMixin):
    """Search options applied when calling `.search` on the corresponding LOM-Service."""

    facets = {
        "right_license": facets.rights_license,
    }


class LOMSearchDraftsOptions(SearchDraftsOptions, SearchOptionsMixin):
    """Search options for drafts search."""

    facets = {
        "right_license": facets.rights_license,
    }


class LOMRecordServiceConfig(RecordServiceConfig, ConfiguratorMixin):
    """Config for LOM record service."""

    # Record and draft class
    draft_cls = LOMDraft
    record_cls = LOMRecord

    # Schemas
    schema = LOMRecordSchema

    # Permission Policy
    permission_policy_cls = FromConfig(
        "LOM_PERMISSION_POLICY", default=LOMRecordPermissionPolicy, import_string=True
    )

    # Search
    search = FromConfigSearchOptions(
        "LOM_SEARCH",
        "LOM_SORT_OPTIONS",
        "LOM_FACETS",
        search_option_cls=LOMSearchOptions,
    )
    search_drafts = FromConfigSearchOptions(
        "LOM_SEARCH_DRAFTS",
        "LOM_SORT_OPTIONS",
        "LOM_FACETS",
        search_option_cls=LOMSearchDraftsOptions,
    )

    # PIDs
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
            if_=RecordLink("{+api}/oer/{id}/files"),
            else_=RecordLink("{+api}/oer/{id}/draft/files"),
        ),
        "latest_html": RecordLink("{+ui}/oer/id/latest", when=is_record),
        "publish": RecordLink("{+api}/oer/{id}/draft/actions/publish", when=is_draft),
        "record_html": RecordLink("{+ui}/oer/{id}", when=is_draft),
        "reserve_doi": RecordLink("{+api}/oer/{id}/draft/pids/doi"),
        "self": ConditionalLink(
            cond=is_record,
            if_=RecordLink("{+api}/oer/{id}"),
            else_=RecordLink("{+api}/oer/{id}/draft"),
        ),
        "self_doi": Link(
            "{+ui}/oer/doi/{+pid_doi}",
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
            if_=RecordLink("{+ui}/oer/{id}"),
            else_=RecordLink("{+ui}/oer/uploads/{id}"),
        ),
    }

    components = FromConfig(
        "LOM_RECORDS_SERVICE_COMPONENTS",
        default=DefaultRecordsComponents,
    )

    links_search = pagination_links("{+api}/lom{?args*}")

    links_search_drafts = pagination_links("{+api}/lom/draft{?args*}")


class LOMDraftFilesServiceConfig(FileServiceConfig, ConfiguratorMixin):
    """Config for LOM draft files service."""

    record_cls = LOMDraft
    permission_action_prefix = "draft_"
    permission_policy_cls = FromConfig(
        "LOM_PERMISSION_POLICY", default=LOMRecordPermissionPolicy, import_string=True
    )

    # links to appear within FileList-result:
    file_links_list = {
        "self": RecordLink("{+api}/oer/{id}/draft/files"),
    }

    # links to appear within the items of FileList-results:
    # (note that, due to `Link.should_render`, some of these links may not appear on items)
    file_links_item = {
        "commit": FileLink("{+api}/oer/{id}/draft/files/{key}/commit"),
        "content": FileLink("{+api}/oer/{id}/draft/files/{key}/content"),
        "iiif_base": FileLink(
            "{+api}/oer/iiif/draft:{id}:{key}", when=is_iiif_compatible
        ),
        "self": FileLink("{+api}/oer/{id}/draft/files/{key}"),
    }


class LOMRecordFilesServiceConfig(FileServiceConfig, ConfiguratorMixin):
    """Config for LOM files service."""

    record_cls = LOMRecord
    permission_policy_cls = FromConfig(
        "LOM_PERMISSION_POLICY", default=LOMRecordPermissionPolicy, import_string=True
    )

    file_links_list = {}
    file_links_item = {
        "iiif_base": FileLink(
            "{+api}/oer/iiif/record:{id}:{key}", when=is_iiif_compatible
        ),
    }
