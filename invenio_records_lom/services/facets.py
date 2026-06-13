# -*- coding: utf-8 -*-
#
# Copyright (C) 2023-2024 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""LOM facets (`facet` is opensearch-lingo for `search-query filter`)."""

from invenio_i18n import gettext as _
from invenio_records_resources.services.records.facets import TermsFacet

rights_license = TermsFacet(
    field="metadata.rights.name.keyword",
    label=_("License"),
)
