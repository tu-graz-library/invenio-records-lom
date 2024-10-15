# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2024 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Config classes for LOMRecordService-objects."""

from types import MappingProxyType

from invenio_drafts_resources.services.records.config import (
    RecordServiceConfig,
    SearchDraftsOptions,
    SearchOptions,
    is_draft,
    is_record,
)
from invenio_indexer.api import RecordIndexer
from invenio_rdm_records.services.config import (
    archive_download_enabled,
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

    def __get__(self, obj, objtype=None) -> dict:  # noqa: ANN001
        """Return dictionary keyed by scheme, with {"name1": provider1, ...}."""
        configs_by_scheme = obj._app.config.get(  # noqa: SLF001
            "LOM_PERSISTENT_IDENTIFIERS",
            {},
        )
        providers = obj._app.config.get(  # noqa: SLF001
            "LOM_PERSISTENT_IDENTIFIER_PROVIDERS",
            [],
        )
        doi_enabled = obj._app.config.get("DATACITE_ENABLED", False)  # noqa: SLF001

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

    def __get__(self, obj, objtype=None) -> list:  # noqa: ANN001
        """Return list of enabled required schemes."""
        configs_by_scheme = obj._app.config.get(  # noqa: SLF001
            "LOM_PERSISTENT_IDENTIFIERS",
            {},
        )
        doi_enabled = obj._app.config.get("DATACITE_ENABLED", False)  # noqa: SLF001

        enabled_schemes = (
            scheme for scheme in configs_by_scheme if scheme != "doi" or doi_enabled
        )

        return [
            scheme
            for scheme in enabled_schemes
            if configs_by_scheme[scheme].get("required", False)
        ]


class LOMSearchOptions(SearchOptions, SearchOptionsMixin):
    """Search options applied when calling .search on the corresponding LOM-Service."""

    facets = MappingProxyType(
        {
            "right_license": facets.rights_license,
        },
    )


class LOMSearchDraftsOptions(SearchDraftsOptions, SearchOptionsMixin):
    """Search options for drafts search."""

    facets = MappingProxyType(
        {
            "right_license": facets.rights_license,
        },
    )


class LOMRecordServiceConfig(RecordServiceConfig, ConfiguratorMixin):
    """Config for LOM record service."""

    # Record and draft class
    draft_cls = LOMDraft
    record_cls = LOMRecord

    indexer_cls = RecordIndexer
    indexer_queue_name = "lom-records"
    draft_indexer_cls = RecordIndexer
    draft_indexer_queue_name = "lom-records-drafts"

    # Schemas
    schema = LOMRecordSchema

    # Permission Policy
    permission_policy_cls = FromConfig(
        "LOM_PERMISSION_POLICY",
        default=LOMRecordPermissionPolicy,
        import_string=True,
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
    links_item = MappingProxyType(
        {
            "archive": ConditionalLink(
                cond=is_record,
                if_=RecordLink(
                    "{+api}/oer/{id}/files-archive",
                    when=archive_download_enabled,
                ),
                else_=RecordLink(
                    "{+api}/oer/{id}/draft/files-archive",
                    when=archive_download_enabled,
                ),
            ),
            "doi": Link(
                "https://doi.org/{+pid_doi}",
                when=has_doi,
                vars=lambda record, var_s: var_s.update(
                    {
                        f"pid_{scheme}": pid["identifier"]
                        for (scheme, pid) in record.pids.items()
                    },
                ),
            ),
            "files": ConditionalLink(
                cond=is_record,
                if_=RecordLink("{+api}/oer/{id}/files"),
                else_=RecordLink("{+api}/oer/{id}/draft/files"),
            ),
            "latest_html": RecordLink("{+ui}/oer/id/latest", when=is_record),
            "publish": RecordLink(
                "{+api}/oer/{id}/draft/actions/publish",
                when=is_draft,
            ),
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
                vars=lambda record, var_s: var_s.update(
                    {
                        f"pid_{scheme}": pid["identifier"]
                        for (scheme, pid) in record.pids.items()
                    },
                ),
            ),
            "self_html": ConditionalLink(
                cond=is_record,
                if_=RecordLink("{+ui}/oer/{id}"),
                else_=RecordLink("{+ui}/oer/uploads/{id}"),
            ),
        },
    )

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
        "LOM_PERMISSION_POLICY",
        default=LOMRecordPermissionPolicy,
        import_string=True,
    )

    # links to appear within FileList-result:
    file_links_list = MappingProxyType(
        {
            "self": RecordLink("{+api}/oer/{id}/draft/files"),
            "archive": RecordLink(
                "{+api}/oer/{id}/draft/files-archive",
                when=archive_download_enabled,
            ),
        },
    )

    # links to appear within the items of FileList-results:
    # (note that, due to `Link.should_render`, some of these links may not appear
    # on items)
    file_links_item = MappingProxyType(
        {
            "commit": FileLink("{+api}/oer/{id}/draft/files/{key}/commit"),
            "content": FileLink("{+api}/oer/{id}/draft/files/{key}/content"),
            "iiif_base": FileLink(
                "{+api}/oer/iiif/draft:{id}:{key}",
                when=is_iiif_compatible,
            ),
            "self": FileLink("{+api}/oer/{id}/draft/files/{key}"),
        },
    )


class LOMRecordFilesServiceConfig(FileServiceConfig, ConfiguratorMixin):
    """Config for LOM files service."""

    record_cls = LOMRecord
    permission_policy_cls = FromConfig(
        "LOM_PERMISSION_POLICY",
        default=LOMRecordPermissionPolicy,
        import_string=True,
    )

    file_links_list = MappingProxyType(
        {
            "archive": RecordLink(
                "{+api}/oer/{id}/files-archive",
                when=archive_download_enabled,
            ),
        },
    )
    file_links_item = MappingProxyType(
        {
            "iiif_base": FileLink(
                "{+api}/oer/iiif/record:{id}:{key}",
                when=is_iiif_compatible,
            ),
        },
    )
