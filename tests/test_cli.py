# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""CLI tests."""

from invenio_records_lom.cli import lom


def test_discover_lom_cli_command(base_app):
    """Test whether `invenio lom`-CLI-command-group can be found."""
    runner = base_app.test_cli_runner()
    result = runner.invoke(lom)
    assert result.exit_code == 0


def test_create_demo_metadata(
    base_app,  # pylint: disable=unused-argument  # only while body commented out
    cli_location,  # pylint: disable=unused-argument
):
    """Test `invenio lom demo`."""
    # TODO: this fails with
    # datacite.errors.DataCiteNotFoundError: {"errors":[{"status":"404","title":"The resource you are looking for doesn't exist."}]}
    # however, it only fails with test-configuration of DATACITE-environment variables
    # the same underlying code works with actual configuration of those variables...

    # runner = base_app.test_cli_runner()
    # result = runner.invoke(
    #     lom,
    #     [
    #         "demo",
    #         "-n",
    #         "1",
    #         "-s",
    #         "42",
    #     ],
    # )
    # assert result.exit_code == 0
