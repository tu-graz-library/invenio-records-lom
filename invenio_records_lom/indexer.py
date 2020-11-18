# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Indexer for Lomrecords."""

from invenio_indexer.api import RecordIndexer

from invenio_records_lom.proxies import Lom


class LomRecordIndexer(RecordIndexer):
    """Lom indexer."""

    record_cls = Lom
