# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Lom Api."""

from __future__ import absolute_import, print_function

from flask import current_app
from invenio_jsonschemas import current_jsonschemas
from invenio_records.api import Record


class LomRecords(Record):
    """Lom record class."""

    @classmethod
    def create(cls, data, id_=None, **kwargs):
        """Create Lom record."""
        data["$schema"] = current_jsonschemas.path_to_url('lom/lom-v1.0.0.json')
        return super(LomRecords, cls).create(data, id_=id_, **kwargs)
