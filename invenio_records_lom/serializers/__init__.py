# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Record serializers.

Think of serializers as the definition of your output formats for records.

The serializers are responsible for transforming the internal JSON for a record into some external representation (e.g. another JSON format or XML).
"""

from invenio_records_rest.serializers.json import JSONSerializer
from invenio_records_rest.serializers.response import (
    record_responsify,
    search_responsify,
)

from ..marshmallow import LomSchemaV1

# Serializers
# ===========
#: JSON serializer definition.

json_v1 = JSONSerializer(LomSchemaV1, replace_refs=True)

# Records-REST serializers
# ========================
#: JSON record serializer for individual records.

json_v1_response = record_responsify(json_v1, "application/json")

#: JSON record serializer for search results.

json_v1_search = search_responsify(json_v1, "application/json")

__all__ = (
    "json_v1",
    "json_v1_response",
    "json_v1_search",
)
