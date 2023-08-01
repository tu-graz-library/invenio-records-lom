# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 Graz University of Technology.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""LOM facets (`facet` is opensearch-lingo for `search-query filter`)."""

# TODO: replace with `from invenio_i18n import gettext as _` after updating to new version
#       this also need be done in some other places...
from flask_babelex import gettext as _
from invenio_records_resources.services.records.facets import TermsFacet


def license_labels(keys):
    """Label licenses."""
    license_mapping = {
        "https://creativecommons.org/licenses/by/4.0": _("CC BY 4.0"),
        "https://creativecommons.org/licenses/by-sa/4.0": _("CC BY-SA 4.0"),
        "https://creativecommons.org/licenses/by-nd/4.0": _("CC BY-ND 4.0"),
        "https://creativecommons.org/licenses/by-nc/4.0": _("CC BY-NC 4.0"),
        "https://creativecommons.org/licenses/by-nc-sa/4.0": _("CC BY-NC-SA 4.0"),
        "https://creativecommons.org/licenses/by-nc-nd/4.0": _("CC BY-NC-ND 4.0"),
    }
    out = {}
    for key in keys:
        search_key = key
        if search_key[-1] == "/":
            search_key = search_key[:-1]
        if search_key[0:5] == "http:":
            search_key = f"https{search_key[4:]}"

        out[key] = license_mapping.get(search_key)

    return out


rights_license = TermsFacet(
    field="metadata.rights.url.keyword",
    label=_("License"),
    value_labels=license_labels,
)
