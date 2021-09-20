# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Submodule for creating demo records."""

from .demo import create_fake_record, create_fake_records

__all__ = (
    "create_fake_record",
    "create_fake_records",
)