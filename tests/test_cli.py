# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""CLI tests."""

from invenio_records_lom.cli import lom


def test_discover_lom_cli_command(base_app):
    runner = base_app.test_cli_runner()
    result = runner.invoke(lom)
    assert result.exit_code == 0


def test_create_demo_metadata(base_app, cli_location):
    """Test "invenio lom demo"."""
    runner = base_app.test_cli_runner()
    result = runner.invoke(
        lom,
        [
            "demo",
            "-n",
            "1",
            "-s",
            "42",
        ],
    )
    assert result.exit_code == 0
