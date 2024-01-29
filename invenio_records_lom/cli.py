# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2024 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Click command-line interface for LOM module."""
from __future__ import annotations

import json
from copy import deepcopy
from importlib import metadata, resources
from importlib.abc import Traversable
from itertools import count

import click
import yaml
from faker import Faker
from flask.cli import with_appcontext
from invenio_access.permissions import system_identity
from invenio_vocabularies.proxies import current_service as vocabulary_service
from invenio_vocabularies.records.models import VocabularyMetadata, VocabularyType
from sqlalchemy.orm.exc import NoResultFound

from .fixtures import publish_fake_record, publish_fake_record_over_celery
from .proxies import current_records_lom
from .records.models import LOMRecordMetadata
from .resources.serializers.schemas import LOMMetadataToOAISchema
from .utils import DotAccessWrapper
from .utils.vocabularies import (
    VocabularyDeleteItem,
    VocabularyImportItem,
    delete_vocabulary,
    delete_vocabulary_entry,
    import_vocabulary,
)


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
        json_ = record.json or {}
        if not json_:
            continue
        pid = json_.get("id") or f"unknown #{next(counter):0>2}"
        json_by_pid[pid] = json_

    if not pids_to_check:
        pids_to_check = json_by_pid.keys()

    for pid in pids_to_check:
        if pid not in json_by_pid:
            click.secho(f"{pid}: could not find a record to this pid", fg="red")
            continue
        try:
            json_ = json_by_pid[pid]
            LOMMetadataToOAISchema().load(json_.get("metadata", {}))
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


#
# vocabularies commands
#
@lom.group()
def vocabularies():
    """CLI-group for `invenio_records_lom`'s flavor of vocabulary commands."""


def echo_import_item(item: VocabularyImportItem):
    """Echo information within `item`."""
    if item.vocabulary_type_created:
        click.secho(f"added vocabulary-type with id {item.vocabulary_id!r}", fg="green")
    else:
        click.echo(f"vocabulary-type for id {item.vocabulary_id!r} already existed")

    click.secho(
        # note: implicit string concatenation
        f"{item.vocabulary_id!r}: "
        f"{len(item.added_entries_ids)} added, "
        f"{len(item.undeleted_entries_ids)} undeleted, "
        f"{len(item.updated_entries_ids)} updated, "
        f"{len(item.unchanged_entries_ids)} left as-is",
        fg="green",
    )


def echo_delete_item(item: VocabularyDeleteItem):
    """Echo information within `item`."""
    if item.vocabulary_type_deleted:
        click.secho(f"deleted vocabulary-type with id {item.vocabulary_id!r}", fg="red")
    else:
        click.echo(f"vocabulary-type for id {item.vocabulary_id!r} already deleted")

    click.secho(
        f"{item.vocabulary_id!r}: {len(item.deleted_entries_ids)} entries deleted",
        fg="red",
    )


@vocabularies.command("list")
@click.argument(
    "vocabulary-id",
    required=False,
    type=str,
)
@with_appcontext
def list_vocabularies(vocabulary_id: str | None):
    """List vocabulary contents.

    \b
    Examples:
      invenio lom vocabularies list
      invenio lom vocabularies list oefos
      invenio lom vocabularies list oefos | grep "comp*"

    Call without arguments to list all registered vocabulary-types.
    Call with the id of a vocabulary-type to list metadata stored for that type.
    """
    if vocabulary_id is None:
        registered_types = VocabularyType.query.order_by(VocabularyType.id).all()
        pid_type_by_id = {row.id: row.pid_type for row in registered_types}
        click.secho(f"number of types: {len(registered_types)}", fg="green")
        for id_, pid_type in pid_type_by_id.items():
            click.echo(f"{pid_type:6} " + click.style(id_, bold=True, fg="blue"))

    else:
        jsons = [row.json for row in VocabularyMetadata.query.all()]
        relevant_jsons = [j for j in jsons if j["type"]["id"] == vocabulary_id]
        click.secho(
            f"number of {vocabulary_id!r} entries: {len(relevant_jsons)}", fg="green"
        )
        for json_ in relevant_jsons:
            data = {k: v for k, v in json_.items() if k in ["title", "props", "tags"]}
            click.echo(click.style(json_["id"], fg="cyan", bold=True) + " " + str(data))

        # check whether `vocabulary_id` has a row in vocabulary_types table
        # absence should still run above code, but output an error
        # error is output last as to become most recent line in terminal
        try:
            VocabularyType.query.filter_by(id=vocabulary_id).one()
        except NoResultFound:
            msg = f"no entry found in vocabularies_types for given id {vocabulary_id!r}"
            click.secho(msg, fg="red", err=True)


@vocabularies.command("import")
@click.option(
    "--vocabulary-id",
    help="name under which the vocabulary can later be read (lowercase, as one word)",
    required=True,
    type=str,
)
@click.option(
    "--pid-type",
    help="PID-type under which to register this vocabulary in `pidstore_pid` (<=6 letters)",
    type=str,
)
@click.option(
    "--file",
    help="path to input YAML file",
    required=True,
    type=click.Path(dir_okay=False, exists=True),
)
@click.option(
    "--force",
    default=False,
    help="whether to overwrite already imported entries",
    is_flag=True,
    type=bool,
)
@with_appcontext
def import_vocabulary_command(
    vocabulary_id: str, pid_type: str, file: str, force: bool
):
    """Import vocabulary from file.

    \b
    Example:
        invenio lom vocabularies import
            --vocabulary-id oefos
            --pid-type oefos
            --file /path/to/oefos.yaml

    `pid_type` is optional if a vocabulary of id `vocabulary_id` was imported before.
    """
    with open(file, encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    import_item = import_vocabulary(
        data,
        vocabulary_id=vocabulary_id,
        pid_type=pid_type,
        overwrite=force,
    )
    echo_import_item(import_item)


@vocabularies.command()
@with_appcontext
def setup():
    """Setup `invenio_records_lom`'s vocabularies."""
    # get invenio_record_lom's entrypoint for vocabulary-fixtures
    (fixture_entrypoint,) = metadata.entry_points(
        group="invenio_rdm_records.fixtures", name="invenio_records_lom"
    )

    # that entrypoint's `.module` is path to a submodule within invenio_records_lom,
    # e.g. "invenio_records_lom.fixtures.data"
    fixture_module_id: str = fixture_entrypoint.module

    # module's need NOT be physical files (could be file-entry in a zip-file, ...)
    # this is abstracted away by `resources.files` and `Traversable`
    directory: Traversable = resources.files(fixture_module_id)
    with directory.joinpath("vocabularies.yaml").open(encoding="utf-8") as file:
        vocabularies_import_info: dict = yaml.safe_load(file)

    # import all invenio_records_lom vocabularies
    for vocabulary_id, info in vocabularies_import_info.items():
        with directory.joinpath(info["data-file"]).open(encoding="utf-8") as file:
            entries = yaml.safe_load(file)
        import_item = import_vocabulary(
            entries,
            vocabulary_id=vocabulary_id,
            pid_type=info["pid-type"],
            overwrite=False,
        )
        echo_import_item(import_item)


@vocabularies.command()
@click.argument(
    "vocabulary-ids",
    nargs=-1,
    required=True,
    type=str,
)
@with_appcontext
def delete(vocabulary_ids: list[str]):
    """Remove vocabulari(es).

    Example: invenio lom vocabularies delete highereducationresourcetypes oefos
    """
    for vocabulary_id in vocabulary_ids:
        delete_item = delete_vocabulary(vocabulary_id)
        echo_delete_item(delete_item)


@vocabularies.command()
@click.option(
    "--vocabulary-id", help="vocabulary to add entry to", required=True, type=str
)
@click.option(
    "--entry-json-str", help="json of the new entry, as a str", required=True, type=str
)
@with_appcontext
def add_entry(vocabulary_id: str, entry_json_str: str):
    """Add entry to vocabulary.

    \b
    Examples:
        invenio lom vocabularies add-entry
            --vocabulary-id oefos
            --entry-json-str "{\\"id\\": \\"name\\", \\"title\\": {\\"en\\": \\"en_title\\"}}"
        invenio lom vocabularies add-entry
            --vocabulary-id oerlicenses
            --entry-json-str "$(< /path/to/entry.json)"

    Note that the entry's json needs to be a dict with at least an "id" member.
    """
    entry_json = json.loads(entry_json_str)
    if VocabularyType.query.filter_by(id=vocabulary_id).one_or_none() is None:
        msg = f"no type found for given vocabulary-id {vocabulary_id!r}"
        click.secho(msg, fg="red")
        return

    jsons = [row.json for row in VocabularyMetadata.query]
    entry_ids_in_db = [
        json["id"] for json in jsons if json["type"]["id"] == vocabulary_id
    ]
    entry_id = entry_json["id"]
    if entry_id in entry_ids_in_db:
        click.secho(f"entry already exists: {entry_id!r}", fg="red")
        return

    entry_json["type"] = vocabulary_id
    vocabulary_service.create(identity=system_identity, data=entry_json)
    click.secho(f"created new entry {entry_id!r} in {vocabulary_id!r}", fg="green")


@vocabularies.command()
@click.option(
    "--vocabulary-id",
    help="the to-be-updated entry's vocabulary-id",
    required=True,
    type=str,
)
@click.option(
    "--entry-id",
    help="the id of the to-be-updated entry within its vocabulary",
    required=True,
    type=str,
)
@click.option(
    "--key",
    help="key to the to-be-up-dated value, supports dot-notation",
    required=True,
    type=str,
)
@click.option("--str-value", help="value to set data at KEY to, used as-is", type=str)
@click.option(
    "--json-value", help="value to set data at KEY to, json-parsed before use", type=str
)
@with_appcontext
def update_entry(
    vocabulary_id: str,
    entry_id: str,
    key: str,
    str_value: str,
    json_value: str,
):
    """Update data within entry in vocabulary.

    \b
    Examples:
        update-entry --vocabulary-id vid --entry-id eid --key props.name --str-value me
        update-entry --vocabulary-id vid --entry-id eid --key tags.[] --str-value new-tag
        update-entry --vocabulary-id vid --entry-id eid --key "" --json-value "$(< file.json)"

    For setting a value to `key`, `DotAccessWrapper` is used internally; hence all its
    features can be used:
    "props.short_name" updates data["props"]["short_name"] (creating "props" if needed).
    "tags.[] appends to tags (creating data["tags"] as a list if needed).
    """
    if (str_value is None and json_value is None) or (
        str_value is not None and json_value is not None
    ):
        click.secho("must give exactly one of '--str-value', '--json-value'", fg="red")
        return
    if str_value is not None:
        value = str_value
    else:
        value = json.loads(json_value)

    vocab_item = vocabulary_service.read(
        identity=system_identity, id_=(vocabulary_id, entry_id)
    )
    dot_access_wrapper = DotAccessWrapper(deepcopy(vocab_item.data))
    dot_access_wrapper[key] = value
    vocabulary_service.update(
        identity=system_identity,
        id_=(vocabulary_id, entry_id),
        data=dot_access_wrapper.data,
    )
    click.secho(
        f"updated entry {entry_id!r} in vocabulary {vocabulary_id!r}", fg="green"
    )


@vocabularies.command()
@click.option(
    "--vocabulary-id",
    help="to-be-deleted entry's vocabulary-id",
    required=True,
    type=str,
)
@click.option(
    "--entry-id", help="to-be-deleted entry's entry-id", required=True, type=str
)
@with_appcontext
def delete_entry(vocabulary_id: str, entry_id: str):
    """Delete entry from vocabulary.

    Example: delete-entry --vocabulary-id oerlicenses --entry-id https://cre.../by/4.0/
    """
    delete_vocabulary_entry(vocabulary_id, entry_id=entry_id)
    click.secho(
        f"deleted entry {entry_id!r} from vocabulary {vocabulary_id!r}", fg="red"
    )


# TODO:
#   - add `invenio lom vocabularies export` as reverse of import?
#   - write test(s) for internals in utils/vocabularies
#   - use vocabularies in:
#     - deposit-page
#     - facets
