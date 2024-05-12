# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2024 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""CLI tests."""

from flask import Flask

from invenio_records_lom.cli import lom


def test_discover_lom_cli_command(base_app: Flask) -> None:
    """Test whether `invenio lom`-CLI-command-group can be found."""
    runner = base_app.test_cli_runner()
    result = runner.invoke(lom)
    assert result.exit_code == 0
