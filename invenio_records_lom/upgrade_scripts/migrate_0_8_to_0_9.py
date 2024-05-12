# -*- coding: utf-8 -*-
#
# Copyright (C) 2023-2024 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Record migration script from invenio-records-lom 0.8 to 0.9.

To upgrade call the whole file from within app-context.
(e.g. via `pipenv run invenio shell \
           /path/to/invenio_records_lom/upgrade_scripts/migrate_0_8_to_0_9.py`)
(e.g. via `pipenv run invenio shell \
           $(find $(pipenv --venv)/lib/*/site-packages/invenio_records_lom \
           -name migrate_0_8_to_0_9.py))`)
"""

from copy import deepcopy

from click import secho
from invenio_db import db

from invenio_records_lom.records.models import LOMDraftMetadata, LOMRecordMetadata


def execute_upgrade() -> None:
    """Execute upgrade from `invenio-records-lom` `v0.8` to `v0.9`."""
    secho('LOM upgrade: adding "$schema"-key to drafts and records', fg="green")

    # upgrade JSONs in database; namely insert "$schema"-key
    schema_key = "$schema"
    schema_str = "local://lomrecords/records/record-v1.0.0.json"

    # update drafts
    for draft in LOMDraftMetadata.query.all():
        old_json = draft.json
        if not old_json:
            continue  # for published/deleted drafts, json is None/empy
        if old_json.get(schema_key):
            continue  # don't update if already has "$schema"-key

        # help SQLAlchemy in noticing a change by creating a new object
        new_json = deepcopy(old_json)

        new_json[schema_key] = schema_str
        draft.json = new_json
        db.session.add(draft)

    # update records
    for record in LOMRecordMetadata.query.all():
        old_json = record.json
        if not old_json:
            continue  # for records with new-version/embargo, json is None/empty
        if old_json.get(schema_key):
            continue  # don't update if already has "$schema"-key

        # help SQLAlchemy in noticing a change by creating a new object
        new_json = deepcopy(old_json)

        new_json[schema_key] = schema_str
        record.json = new_json
        db.session.add(record)

    db.session.commit()
    secho('Successfully added "$schema"-key to drafts and records!', fg="green")
    secho(
        "NOTE: this only updated the SQL-database, call `invenio lom reindex` to update opensearch-indices",
        fg="red",
    )


if __name__ == "__main__":
    # gets executed when file is called directly, but not when imported
    execute_upgrade()
