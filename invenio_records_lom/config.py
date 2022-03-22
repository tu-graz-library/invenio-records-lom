# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Default configuration."""

import idutils
from flask_babelex import gettext as _
from invenio_rdm_records.services.pids import providers

from .resources.serializers import LOMToDataCite44Serializer

LOM_ROUTES = {
    "record_detail": "/lom/<pid_value>",
    "record_export": "/lom/<pid_value>/export/<export_format>",
    "record_file_preview": "/lom/<pid_value>/preview/<path:filename>",
    "record_file_download": "/lom/<pid_value>/files/<path:filename>",
    "record_from_pid": "/lom/<any({schemes}):pid_scheme>/<path:pid_value>",
    "record_latest": "/lom/<pid_value>/latest",
}

LOM_RECORD_EXPORTERS = {
    "json": {
        "name": _("JSON"),
        "serializer": "flask_resources.serializers:JSONSerializer",
    },
}

LOM_RESOURCE_TYPES = [
    "course",
    "unit",
    "file",
    "link",
]

LOM_PUBLISHER = "Graz University of Technology"

#
# Persistent identifiers configuration
#
LOM_PERSISTENT_IDENTIFIER_PROVIDERS = [
    # DataCite DOI provider
    providers.DataCitePIDProvider(
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
