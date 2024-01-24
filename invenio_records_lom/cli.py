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


# TODO: might move this to another file, hence imports are down here for the time...
import dataclasses
from copy import copy

import yaml
from invenio_records_resources.services.uow import unit_of_work
from invenio_vocabularies.proxies import current_service as vocabulary_service
from invenio_vocabularies.records.models import VocabularyMetadata, VocabularyType
from sqlalchemy.orm.exc import NoResultFound


# TODO: type-annotations
# TODO: use identity of current user vs system_identity?
@lom.group()
def vocabularies():
    """CLI-group for `invenio_records_lom`'s flavor of vocabulary commands."""


@vocabularies.command("list")
@click.argument(
    "type-id",
    help="`type-id` of a vocabulary [optional].",
    required=False,
    type=click.STRING,
)
@with_appcontext
def list_vocabularies(type_id: str | None = None):
    """List vocabulary contents.

    call without arguments to show all registered vocabulary-types
    call with a vocabulary-type as argument to list metadata stored for that type

    example calls:
    invenio lom vocabularies list
    invenio lom vocabularies list relationtypes | grep "comp*"
    """
    # TODO: put lom-specifc vocabulary-type into docstring-example
    if type_id is None:
        # TODO: also echo pid-type
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


@dataclasses.dataclass
class VocabularyImportItem:
    """Holds information on work done, similar to invenio's `Item`-classes."""

    type_id: str
    pid_type: str
    type_created: bool = False
    added_ids: list[str] = dataclasses.field(default_factory=list)
    unchanged_ids: list[str] = dataclasses.field(default_factory=list)
    updated_ids: list[str] = dataclasses.field(default_factory=list)


def echo_import_item(item: VocabularyImportItem):
    """Echo information within `item`."""
    if item.type_created:
        click.secho(f"added vocabulary-type {item.type_id!r}", fg="green")
    else:
        click.secho(f"vocabulary-type {item.type_id!r} already existed")
    click.secho(
        # note: implicit string concatenation
        f"{item.type_id}: "
        f"{len(item.added_ids)} added, "
        f"{len(item.updated_ids)} updated, "
        f"{len(item.unchanged_ids)} left as-is",
        fg="green",
    )


# TODO: this function isn't CLI-specific, so it should be moved to another location:
@unit_of_work()
def import_vocabulary(
    entries: list[dict],
    /,  # @unit_of_work requires at least one positional arg in functions it decorates
    type_id: str,
    pid_type: str,
    overwrite: bool = False,
    uow=None,
) -> VocabularyImportItem:
    """Import a vocabulary into database.

    If entries of this `type_id` were not imported before, then this vocabulary is
    registered in `vocabularies_types` table.
    Then, every entry in `entries` is imported to `vocabularies_metadata` table.
    When encountering an already imported entry, `overwrite` signals whether to keep
    the currently imported entry or to overwrite with the passed-in entry.

    sample call:

    .. code-block:: python

        import_vocabulary(
            entries=[{"id": "id-of-entry", "title": {"en": "Title"}}, ...],
            type_id="nameoftype",
            pid_type="nmoftp",
            overwrite=False,
        )

    :param list[dict] entries: entries to import
    :param str type_id: all lowercase as-one-word name of the vocabulary
    :param str pid_type: for referencing vocabulary from `pidstore_pid` table
    :param bool overwrite: whether to overwrite already imported entries
    """
    #
    result_item = VocabularyImportItem(type_id=type_id, pid_type=pid_type)
    pid_type_in_db: str = (
        VocabularyType.query.filter_by(id=type_id)
        .with_entities(VocabularyType.pid_type)
        .scalar()
    )

    # checks as to fail early
    for entry in entries:
        if "id" not in entry:
            raise ValueError(f"entry in the passed-in `entries` has no id: {entry!r}")
    if pid_type_in_db is not None and pid_type_in_db != pid_type:
        raise ValueError(
            f"passed pid-type differs from registered: {pid_type_in_db!r} (db) / {pid_type!r} (passed)"
        )
    if not 0 < len(pid_type) <= 6:
        raise ValueError(f"pid-types need to be 1 to 6 letters long: was {pid_type!r}")

    # if new `type_id`, register it
    if pid_type_in_db is None:
        vocabulary_service.create_type(
            identity=system_identity, id=type_id, pid_type=pid_type, uow=uow
        )
        result_item.type_created = True

    # load entries
    existing_entry_ids = {
        row.json["id"]
        for row in VocabularyMetadata.query.all()
        if row.json["type"]["id"] == type_id
    }
    for entry in entries:
        entry = copy(entry)  # shallow copy suffices
        entry["type"] = type_id
        if entry["id"] not in existing_entry_ids:
            vocabulary_service.create(identity=system_identity, data=entry, uow=uow)
            result_item.added_ids.append(entry["id"])
        elif overwrite:
            vocabulary_service.update(identity=system_identity, data=entry, uow=uow)
            result_item.updated_ids.append(entry["id"])
        else:
            result_item.unchanged_ids.append(entry["id"])

    return result_item


@vocabularies.command("import")
@click.option(
    "--type-id",
    help="Name under which the vocabulary can later be read (lowercase, as one word).",
    required=True,
    type=click.STRING,
)
@click.option(
    "--pid-type",
    help="PID type under which to register this vocabulary in `pidstore_pid` (<=6 letters).",
    required=True,
    type=click.STRING,
)
@click.option(
    "--file",
    help="YAML file to read data from.",
    type=click.Path(dir_okay=False, exists=True),
)
@click.option(
    "--force",
    default=False,
    help="Whether to overwrite already imported entries.",
    is_flag=True,
    type=click.STRING,
)
@with_appcontext
def import_vocabulary_command(type_id, pid_type, file, force):
    """Import a vocabulary."""
    with open(file, encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    import_item = import_vocabulary(
        data,
        type_id=type_id,
        pid_type=pid_type,
        overwrite=force,
    )
    echo_import_item(import_item)


@vocabularies.command()
def setup(force):
    # get vocabularies.yaml file from entrypoint
    # for each vocabulary as specified in file:
    #   - call import_vocabulary
    #   - echo that import
    pass


# TODO:
# C reate:
#   vocabs: vocabularies import
#   single entries: vocabularies entries add
# R ead:
#   vocabs: vocabularies list [<type>]
#   single entries: vocabularies list <type> | grep ...
# U pdate:
#   vocab overwrite entries: vocabularies import --force
#   entry overwrite: vocabularies entries ? (same func as add, with --force?)
# D elete:
#   vocab delete (whole type): ?
#   entry delete (to remove from Dropdown-options): ?
# backup:
#   necessary?
