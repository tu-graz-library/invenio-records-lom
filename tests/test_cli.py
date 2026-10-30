# SPDX-FileCopyrightText: 2021-2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""CLI tests."""

from flask import Flask

from invenio_records_lom.cli import lom


def test_discover_lom_cli_command(base_app: Flask) -> None:
    """Test whether `invenio lom`-CLI-command-group can be found."""
    runner = base_app.test_cli_runner()
    result = runner.invoke(lom)
    assert result.exit_code == 2
