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


# TODO: might move this another file, hence imports are down here for the time...
from collections import Counter

import yaml
from invenio_records_resources.services.uow import unit_of_work
from invenio_vocabularies.proxies import current_service as vocabulary_service
from invenio_vocabularies.records.models import VocabularyMetadata, VocabularyType
from invenio_vocabularies.services import VocabulariesService
from sqlalchemy.orm.exc import NoResultFound


# TODO: type-annotations
# TODO: use identity of current user vs system_identity?
@lom.group()
def vocabularies():
    """CLI-group for `invenio_records_lom`'s flavor of vocabulary commands."""


@vocabularies.command()
@click.argument("type_id", required=False)
@with_appcontext
def ls(type_id=None):
    """List vocabulary contents.

    call without arguments to show all registered vocabulary-types
    call with a vocabulary-type as argument to list metadata stored for that type

    example calls:
    invenio lom vocabularies ls
    invenio lom vocabularies ls relationtypes | grep "comp*"
    """
    # TODO: put lom-specifc vocabulary-type into docstring-example
    if type_id is None:
        registered_type_ids = sorted(entry.id for entry in VocabularyType.query.all())
        click.secho(f"number of types: {len(registered_type_ids)}", fg="green")
        for registered_type_id in registered_type_ids:
            click.secho(registered_type_id, bold=True, fg="blue")
    else:
        jsons = [entry.json for entry in VocabularyMetadata.query.all()]
        relevant_jsons = [json_ for json_ in jsons if json_["type"]["id"] == type_id]
        click.secho(f"number of '{type_id}' entries: {len(relevant_jsons)}", fg="green")
        for json_ in relevant_jsons:
            data = {k: v for k, v in json_.items() if k in ["title", "props", "tags"]}
            click.echo(click.style(json_["id"], fg="cyan", bold=True) + " " + str(data))

        # check whether requested `type_id` is registered in `vocabularies_types` table
        # non-registration should still run above code, but output an error
        # errors should be output last on CLIs (most recent line in terminal)
        try:
            VocabularyType.query.filter_by(id=type_id).one()
        except NoResultFound:
            msg = f"requested type-id `{type_id}` not found in vocabularies_types table"
            click.secho(msg, fg="red", err=True)


@unit_of_work()
def import_vocabulary(data: list[dict], type_id, pid_type, overwrite: bool, uow=None):
    # TODO: rename `data` (confusable with service-methods' kwarg of same name)
    # TODO: can this be made independent of CLI? (no calling click.secho)

    # if new type_id, register it
    type_ids = {entry.id for entry in VocabularyType.query.all()}
    if type_id not in type_ids:
        vocabulary_service.create_type(
            identity=system_identity, id=type_id, pid_type=pid_type, uow=uow
        )
        click.secho(f"added vocabulary-type {type_id}", fg="green")
    else:
        click.secho(f"vocabulary-type {type_id} already added")

    # load
    existing_entry_ids = {
        e.id for e in VocabularyMetadata.query.all() if e.json["type"]["id"] == type_id
    }
    counter = Counter()
    for entry in data:
        if "id" not in entry:
            # malformed entry, cannot be entered into database
            # TODO: just immmediately raise?
            click.secho()  # TODO
            counter[""] += 1  # TODO
            continue
        entry = entry.copy()  # TODO: copy.copy(entry) ?
        entry["type"] = type_id
        if entry["id"] in existing_entry_ids and overwrite:
            vocabulary_service.update(identity=system_identity, data=entry, uow=uow)
            counter["updated"] += 1
        elif entry["id"] in existing_entry_ids and not overwrite:
            counter["passed"] += 1
        else:
            vocabulary_service.create(identity=system_identity, data=entry, uow=uow)
            counter["added"] += 1
    click.secho("<type>: <x-num> added, <y-num> updated, <z-num> ???")


@vocabularies.command("import")
# TODO: options
@with_appcontext
def import_command(type_id, pid_type, file, force):
    with open(file, encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    import_vocabulary(data=data, type_id=type_id, pid_type=pid_type, overwrite=force)
    # from file
    # from fixtures folder (?)


@vocabularies.command()
def setup():
    # get vocabularies.yaml file from entrypoint
    # for each vocabulary as specified in file: call import_voabulary
    pass


# TODO: update, create, backup funcs
