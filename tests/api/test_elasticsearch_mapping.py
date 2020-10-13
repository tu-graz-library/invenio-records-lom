# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test Elasticsearch Mapping."""

import uuid

import pytest
from invenio_indexer.api import RecordIndexer
from invenio_jsonschemas import current_jsonschemas
from invenio_pidstore import current_pidstore

# TODO: use from invenio_records_files.api import Record
from invenio_records.api import Record
from invenio_records_rest.schemas.fields import DateString, SanitizedUnicode
from marshmallow.fields import Bool, Integer, List


@pytest.fixture()
def minimal_record(appctx, minimal_record):
    data = {
        '$schema': (
            current_jsonschemas.path_to_url('lom/lom-v1.0.0.json')
        ),
        'publication_date': '2020-06-01'
    }
    minimal_record.update(data)
    return minimal_record


def assert_unordered_equality(array_dict1, array_dict2):
    array1 = sorted(array_dict1, key=lambda d: d['key'])
    array2 = sorted(array_dict2, key=lambda d: d['key'])
    assert array1 == array2
