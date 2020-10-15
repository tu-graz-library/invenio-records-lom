# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Default configuration."""

from __future__ import absolute_import, print_function

from invenio_indexer.api import RecordIndexer
from invenio_records_rest.utils import allow_all, check_elasticsearch
from invenio_search import RecordsSearch

from .api import LomRecords

RECORDS_REST_ENDPOINTS = {
    'lomid': dict(
        pid_type='lomid',
        pid_minter='lomid',
        pid_fetcher='lomid',
        default_endpoint_prefix=True,
        record_class=LomRecords,
        search_class=RecordsSearch,
        indexer_class=RecordIndexer,
        search_index='lomrecords',
        search_type=None,
        record_serializers={
            'application/json': ('invenio_records_lom.serializers'
                                 ':json_v1_response'),
        },
        search_serializers={
            'application/json': ('invenio_records_lom.serializers'
                                 ':json_v1_search'),
        },
        record_loaders={
            'application/json': ('invenio_records_lom.loaders'
                                 ':json_v1'),
        },
        list_route='/lom',
        item_route='/lom/<pid(lomid):pid_value>',
        default_media_type='application/json',
        max_result_window=10000,
        error_handlers=dict(),
        create_permission_factory_imp=allow_all,
        read_permission_factory_imp=check_elasticsearch,
        update_permission_factory_imp=allow_all,
        delete_permission_factory_imp=allow_all,
    ),
}
"""REST API for invenio-records-lom."""

RECORDS_UI_ENDPOINTS = {
    'lom': {
        'pid_type': 'lomid',
        'route': '/lom/<pid_value>',
        'template': 'invenio_records_lom/record.html',
    },
}
"""Records UI for invenio-records-lom."""

SEARCH_UI_JSTEMPLATE_RESULTS = 'templates/invenio_records_lom/results.html'
"""Result list template."""

PIDSTORE_RECID_FIELD = 'id'

INVENIO_RECORDS_LOM_ENDPOINTS_ENABLED = True
"""Enable/disable automatic endpoint registration."""
