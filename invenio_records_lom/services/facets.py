# -*- coding: utf-8 -*-
#
# Copyright (C) 2023-2024 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""LOM facets (`facet` is opensearch-lingo for `search-query filter`)."""

from invenio_i18n import gettext as _
from invenio_records_resources.services.records.facets import TermsFacet


def license_labels(keys: list) -> dict:
    """Label licenses.

    ATTENTION: # noqa
    this should be a temporary solution. the real solution should be to fix the
    metadata within the database.

    """
    license_mapping = {
        "https://creativecommons.org/publicdomain/zero/1.0/": _("CC0 1.0"),
        "https://creativecommons.org/licenses/by/4.0/": _("CC BY 4.0"),
        "https://creativecommons.org/licenses/by-sa/4.0/": _("CC BY-SA 4.0"),
        "https://creativecommons.org/licenses/by-nd/4.0/": _("CC BY-ND 4.0"),
        "https://creativecommons.org/licenses/by-nc/4.0/": _("CC BY-NC 4.0"),
        "https://creativecommons.org/licenses/by-nc-sa/4.0/": _("CC BY-NC-SA 4.0"),
        "https://creativecommons.org/licenses/by-nc-nd/4.0/": _("CC BY-NC-ND 4.0"),
    }
    out = {}
    for key in keys:
        search_key = key
        if search_key[-1] != "/":
            search_key += "/"
        if search_key[0:5] == "http:":
            search_key = f"https{search_key[4:]}"

        out[key] = license_mapping.get(search_key)

    return out


rights_license = TermsFacet(
    field="metadata.rights.url.keyword",
    label=_("License"),
    value_labels=license_labels,
)
