# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Minter tests."""

import uuid

import pytest

from invenio_records_lom.minters import lom_pid_minter


def test_lom_pid_minter(base_app, db):
    """Test legacy recid minter."""
    with base_app.app_context():
        rec_uuid = uuid.uuid4()
        data = {}

        pid = lom_pid_minter(rec_uuid, data)

        assert pid
        assert pid.object_type == "rec"
        assert pid.object_uuid == rec_uuid
