# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Click command-line interface for LOM module."""

import click
from flask.cli import with_appcontext

from .fixtures import create_fake_records


@click.group()
def lom():
    """CLI-group for "invenio lom" commands."""
    pass


@lom.command()
@with_appcontext
@click.option(
    "--number",
    "-n",
    default=100,
    show_default=True,
    type=int,
    help="Number of records to be created.",
)
@click.option("--seed", "-s", default=42, type=int, help="Seed for RNG.")
def demo(number, seed):
    """Create `number` fake LOM records for demo purposes."""
    click.secho(f"Creating {number} LOM demo records", fg="green")
    for lom in create_fake_records(number, seed):
        pass
    click.secho("Created LOM records!", fg="green")
