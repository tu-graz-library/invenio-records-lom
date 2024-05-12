# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2024 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Default configuration."""

import idutils
from celery.schedules import crontab
from invenio_i18n import gettext as _
from invenio_rdm_records.services.pids import providers
from invenio_stats.aggregations import StatAggregator
from invenio_stats.contrib.event_builders import build_file_unique_id
from invenio_stats.processors import EventsIndexer, anonymize_user, flag_robots
from invenio_stats.queries import TermsQuery

from .resources.serializers import LOMToDataCite44Serializer
from .services import facets
from .services.permissions import LOMRecordPermissionPolicy
from .services.pids import LOMDataCitePIDProvider
from .utils import build_record_unique_id

LOM_BASE_TEMPLATE = "invenio_records_lom/base.html"

#
# Permission Configuration
#
LOM_PERMISSION_POLICY = LOMRecordPermissionPolicy

#
# Search Configuration
#
LOM_FACETS = {
    "rights_license": {
        "facet": facets.rights_license,
        "ui": {
            # these fields will be available to the React search-app
            # namely, the overridable `BucketAggregation` component gets these
            "field": "metadata.rights.url",
        },
    },
}

LOM_SORT_OPTIONS = {
    "bestmatch": {
        "title": _("Best match"),
        "fields": ["_score"],  # opensearch defaults to desc on `_score` field
    },
    "newest": {
        "title": _("Newest"),
        "fields": ["-created"],
    },
    "mostviewed": {
        "title": _("Most viewed"),
        "fields": ["-stats.all_versions.unique_views"],
    },
    "mostdownloaded": {
        "title": _("Most downloaded"),
        "fields": ["-stats.all_versions.unique_downloads"],
    },
}

LOM_SEARCH = {
    "sort": [
        "bestmatch",
        "newest",
        "mostviewed",
        "mostdownloaded",
    ],
    "facets": [  # which facets to activate, see `LOM_FACETS` for facet-configuration
        "rights_license",
    ],
}
"""Record search configuration."""

LOM_SEARCH_DRAFTS = {
    "sort": ["bestmatch", "newest"],
    "facets": [  # which facets to activate, see `LOM_FACETS` for facet-configuration
        "rights_license",
    ],
}

#
# HTML-Request Configuration
#
LOM_ROUTES = {
    # the blueprint prefixes `/oer` to these routes
    "uploads": "/uploads",
    "deposit_create": "/uploads/new",
    "deposit_edit": "/uploads/<pid_value>",
    "record_detail": "/<pid_value>",
    "record_export": "/<pid_value>/export/<export_format>",
    "record_file_preview": "/<pid_value>/preview/<path:filename>",
    "record_file_download": "/<pid_value>/files/<path:filename>",
    "record_from_pid": "/<any({schemes}):pid_scheme>/<path:pid_value>",
    "record_latest": "/<pid_value>/latest",
    "record_search": "/search",
}

LOM_RECORD_EXPORTERS = {
    "json": {
        "name": _("JSON"),
        "serializer": "flask_resources.serializers:JSONSerializer",
        "content-type": "application/json",
        "filename": "{id}.json",
    },
}

#
# Schema Configuration
#
LOM_RESOURCE_TYPES = [
    "course",
    "unit",
    "file",
    "link",
    "upload",
]

LOM_PUBLISHER = "Graz University of Technology"

#
# Persistent identifiers configuration
#
LOM_PERSISTENT_IDENTIFIER_PROVIDERS = [
    # DataCite DOI provider
    LOMDataCitePIDProvider(
        "datacite",
        client=providers.DataCiteClient(
            "datacite",
            config_prefix="DATACITE",
        ),
        serializer=LOMToDataCite44Serializer(),
        label=_("DOI"),
    ),
    # DOI provider for externally managed DOIs
    providers.ExternalPIDProvider(
        "external",
        "doi",
        validators=[providers.BlockedPrefixes(config_names=["DATACITE_PREFIX"])],
        label=_("DOI"),
    ),
    # OAI provider
    providers.OAIPIDProvider(
        "oai",
        label=_("OAI ID"),
    ),
]
"""A list of configured persistent identifier providers.

ATTENTION: All providers (and clients) takes a name as the first parameter.
This name is stored in the database and used in the REST API in order to
identify the given provider and client.

The name is further used to configure the desired persistent identifiers (see
``LOM_PERSISTENT_IDENTIFIERS`` below)
"""


LOM_PERSISTENT_IDENTIFIERS = {
    # DOI automatically removed if DATACITE_ENABLED is False.
    "doi": {
        "providers": ["datacite", "external"],
        "required": True,
        "label": _("DOI"),
        "validator": idutils.is_doi,
        "normalizer": idutils.normalize_doi,
    },
    "oai": {
        "providers": ["oai"],
        "required": True,
        "label": _("OAI"),
    },
}
"""The configured persistent identifiers for records.

.. code-block:: python

    "<scheme>": {
        "providers": ["<default-provider-name>", "<provider-name>", ...],
        "required": True/False,
    }
"""


# Statistics configuration

LOM_STATS_CELERY_TASKS = {
    # indexing of statistics events & aggregations
    "lom-stats-process-events": {
        "task": "invenio_stats.tasks.process_events",
        "args": [("lom-record-view", "lom-file-download")],
        "schedule": crontab(
            minute="15,45",
        ),  # Every hour at minute 15 and 45
    },
    "lom-stats-aggregate-events": {
        "task": "invenio_stats.tasks.aggregate_events",
        "args": [
            (
                "lom-record-view-agg",
                "lom-file-download-agg",
            ),
        ],
        "schedule": crontab(minute=7),  # Every hour at minute 7
    },
    "lom-reindex-stats": {
        "task": "invenio_records_lom.services.tasks.lom_reindex_stats",
        "args": [
            (
                "stats-lom-record-view",
                "stats-lom-file-download",
            ),
        ],
        "schedule": crontab(minute="20"),
    },
}

# Invenio-Stats
# =============
# See https://invenio-stats.readthedocs.io/en/latest/configuration.html

LOM_STATS_EVENTS = {
    "lom-file-download": {
        "templates": "invenio_records_lom.records.statistics.templates.events.lom_file_download",
        "event_builders": [
            "invenio_rdm_records.resources.stats.file_download_event_builder",
            "invenio_rdm_records.resources.stats.check_if_via_api",
        ],
        "cls": EventsIndexer,
        "params": {
            "preprocessors": [flag_robots, anonymize_user, build_file_unique_id],
        },
    },
    "lom-record-view": {
        "templates": "invenio_records_lom.records.statistics.templates.events.lom_record_view",
        "event_builders": [
            "invenio_rdm_records.resources.stats.record_view_event_builder",
            "invenio_rdm_records.resources.stats.check_if_via_api",
            "invenio_rdm_records.resources.stats.drop_if_via_api",
        ],
        "cls": EventsIndexer,
        "params": {
            "preprocessors": [flag_robots, anonymize_user, build_record_unique_id],
        },
    },
}

LOM_STATS_AGGREGATIONS = {
    "lom-file-download-agg": {
        "templates": "invenio_records_lom.records.statistics.templates.aggregations.aggr_lom_file_download",
        "cls": StatAggregator,
        "params": {
            "event": "lom-file-download",
            "field": "unique_id",
            "interval": "day",
            "index_interval": "month",
            "copy_fields": {
                "file_id": "file_id",
                "file_key": "file_key",
                "bucket_id": "bucket_id",
                "recid": "recid",
                "parent_recid": "parent_recid",
            },
            "metric_fields": {
                "unique_count": (
                    "cardinality",
                    "unique_session_id",
                    {"precision_threshold": 1000},
                ),
                "volume": ("sum", "size", {}),
            },
        },
    },
    "lom-record-view-agg": {
        "templates": "invenio_records_lom.records.statistics.templates.aggregations.aggr_lom_record_view",
        "cls": StatAggregator,
        "params": {
            "event": "lom-record-view",
            "field": "unique_id",
            "interval": "day",
            "index_interval": "month",
            "copy_fields": {
                "recid": "recid",
                "parent_recid": "parent_recid",
                "via_api": "via_api",
            },
            "metric_fields": {
                "unique_count": (
                    "cardinality",
                    "unique_session_id",
                    {"precision_threshold": 1000},
                ),
            },
            "query_modifiers": [lambda query, **_: query.filter("term", via_api=False)],
        },
    },
}

LOM_STATS_QUERIES = {
    "lom-record-view": {
        "cls": TermsQuery,
        "permission_factory": None,
        "params": {
            "index": "stats-lom-record-view",
            "doc_type": "lom-record-view-day-aggregation",
            "copy_fields": {
                "recid": "recid",
                "parent_recid": "parent_recid",
            },
            "query_modifiers": [],
            "required_filters": {
                "recid": "recid",
            },
            "metric_fields": {
                "views": ("sum", "count", {}),
                "unique_views": ("sum", "unique_count", {}),
            },
        },
    },
    "lom-record-view-all-versions": {
        "cls": TermsQuery,
        "permission_factory": None,
        "params": {
            "index": "stats-lom-record-view",
            "doc_type": "lom-record-view-day-aggregation",
            "copy_fields": {
                "parent_recid": "parent_recid",
            },
            "query_modifiers": [],
            "required_filters": {
                "parent_recid": "parent_recid",
            },
            "metric_fields": {
                "views": ("sum", "count", {}),
                "unique_views": ("sum", "unique_count", {}),
            },
        },
    },
    "lom-record-download": {
        "cls": TermsQuery,
        "permission_factory": None,
        "params": {
            "index": "stats-lom-file-download",
            "doc_type": "lom-file-download-day-aggregation",
            "copy_fields": {
                "recid": "recid",
                "parent_recid": "parent_recid",
            },
            "query_modifiers": [],
            "required_filters": {
                "recid": "recid",
            },
            "metric_fields": {
                "downloads": ("sum", "count", {}),
                "unique_downloads": ("sum", "unique_count", {}),
                "data_volume": ("sum", "volume", {}),
            },
        },
    },
    "lom-record-download-all-versions": {
        "cls": TermsQuery,
        "permission_factory": None,
        "params": {
            "index": "stats-lom-file-download",
            "doc_type": "lom-file-download-day-aggregation",
            "copy_fields": {
                "parent_recid": "parent_recid",
            },
            "query_modifiers": [],
            "required_filters": {
                "parent_recid": "parent_recid",
            },
            "metric_fields": {
                "downloads": ("sum", "count", {}),
                "unique_downloads": ("sum", "unique_count", {}),
                "data_volume": ("sum", "volume", {}),
            },
        },
    },
}

LOM_ALLOW_METADATA_ONLY_RECORDS = True
"""Allow users to publish metadata-only records."""

LOM_ALLOW_RESTRICTED_RECORDS = True
"""Allow users to set restricted/private records."""
