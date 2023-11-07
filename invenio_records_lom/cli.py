# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Click command-line interface for LOM module."""
from __future__ import annotations

from itertools import count

import click
from faker import Faker
from flask.cli import with_appcontext
from invenio_access.permissions import system_identity

from .fixtures import publish_fake_record, publish_fake_record_over_celery
from .proxies import current_records_lom
from .records.models import LOMRecordMetadata
from .resources.serializers.schemas import LOMMetadataToOAISchema


@click.group()
def lom():
    """CLI-group for "invenio lom" commands."""


@lom.command("rebuild-index")
@with_appcontext
def rebuild_index():
    """Reindex all drafts, records."""
    click.secho("Reindexing records and drafts...", fg="green")

    rec_service = current_records_lom.records_service
    rec_service.rebuild_index(identity=system_identity)

    click.secho("Reindexed records!", fg="green")


@lom.command()
@with_appcontext
@click.option(
    "--pid",
    "-p",
    "pids_to_check",
    default=[],
    multiple=True,
    type=str,
    help="PIDs to check. Argument can be used multiple times. If never used, check all records.",
)
def check(pids_to_check: tuple[str]):
    """Check records in SQL-database against marshmallow-schema for OAI.

    Note: this does not guarantee by itself that OAI-PMH API works correctly, since
    (1) Records in opensearch might not mirror records in SQL-database, call `invenio lom reindex` to remedy this.
    (2) Records that pass OAI-schema verification might still not play nicely with OAI-PMH harvesters
    That said, passing OAI-schema *is* a prerequisite for OAI-PMH API working correctly
    """
    json_by_pid = {}
    counter = count()  # running count to create differing unkwown pids
    for record in LOMRecordMetadata.query.all():
        json = record.json or {}
        if not json:
            continue
        pid = json.get("id") or f"unknown #{next(counter):0>2}"
        json_by_pid[pid] = json

    if not pids_to_check:
        pids_to_check = json_by_pid.keys()

    for pid in pids_to_check:
        if pid not in json_by_pid:
            click.secho(f"{pid}: could not find a record to this pid", fg="red")
            continue
        try:
            json = json_by_pid[pid]
            LOMMetadataToOAISchema().load(json.get("metadata", {}))
            click.secho(f"{pid}: Success", fg="green")
        except Exception as e:  # pylint: disable=broad-exception-caught
            click.secho(f"{pid}: {e!r}", fg="red")


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
@click.option(
    "--backend",
    "-b",
    default=False,
    type=bool,
    is_flag=True,
    help="Create in backend for large datasets",
)
def demo(number, seed, backend):
    """Publish `number` fake LOM records to the database, for demo purposes."""
    click.secho(f"Creating {number} LOM demo records", fg="green")

    fake = Faker()
    Faker.seed(seed)

    for _ in range(number):
        if backend:
            publish_fake_record_over_celery(fake)
        else:
            publish_fake_record(fake)

    click.secho("Published fake LOM records to the database!", fg="green")


@lom.command()
@with_appcontext
def reindex():
    """Reindex all published records from SQL-database in opensearch-indices."""
    click.secho("Reindexing LOM records...", fg="green")

    record_ids = [
        record.json["id"]
        for record in LOMRecordMetadata.query.all()
        if record.json and "id" in record.json
    ]

    service = current_records_lom.records_service
    indexer = service.indexer
    for record_id in record_ids:
        record_api_object = service.record_cls.pid.resolve(record_id)
        indexer.index(record_api_object)

    click.secho("Successfully reindexed LOM records!", fg="green")
