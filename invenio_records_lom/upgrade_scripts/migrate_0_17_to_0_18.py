# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Record migration script from invenio-records-lom v0.17 to v0.18.

To upgrade, call the whole file from within app-context.
(e.g. via `pipenv run invenio shell \
           /path/to/invenio_records_lom/upgrade_scripts/migrate_0_17_to_0_18.py`)
(e.g. via `pipenv run invenio shell \
           $(find $(pipenv --venv)/lib/*/site-packages/invenio_records_lom \
           -name migrate_0_17_to_0_18.py))`)
"""

from copy import deepcopy

from click import secho
from invenio_db import db

from invenio_records_lom.records.api import LOMDraft, LOMRecord


def execute_upgrade() -> None:
    """Exceute upgrade from `invenio-records-lom` `v0.17` to `v0.18`."""
    secho(
        "LOM upgrade: ensuring `metadata.educational.learningresourcetype` is a list",
        fg="green",
    )

    def get_new_json(old_json: dict) -> dict | None:
        """Get updated json from current json.

        if update is necessary, return updated JSON
        otherwise, return `None`
        """
        current_learningresourcetype = (
            old_json.get("metadata", {})
            .get("educational", {})
            .get("learningresourcetype")
        )
        if current_learningresourcetype is None:
            # no learningresourcetype (which is allowed) - nothing to update
            return None
        if isinstance(current_learningresourcetype, list):
            # already a list (which is correct) - no need to update
            return None

        # not a list-of-things but rather a thing itself - pack into list
        new_json = deepcopy(old_json)
        new_json["metadata"]["educational"]["learningresourcetype"] = [
            current_learningresourcetype,
        ]

        return new_json

    # update drafts
    for draft in LOMDraft.model_cls.query.all():
        old_json = draft.json
        if not old_json:
            continue  # for published/deleted drafts, json is None/empty

        new_json = get_new_json(old_json)
        if new_json is None:
            # `None` means "no update necessary"
            continue

        draft.json = new_json
        db.session.merge(draft)

    # update records
    for record in LOMRecord.model_cls.query.all():
        old_json = record.json
        if not old_json:
            continue  # for records with new-version/embargo, json is None/empty

        new_json = get_new_json(old_json)
        if new_json is None:
            # `None` means "no update necessary"
            continue

        record.json = new_json
        db.session.merge(record)

    db.session.commit()
    secho(
        "Successfully turned `metadata.educational.learningresourcetype` into a list where necessary!",
        fg="green",
    )
    secho(
        "NOTE: this only updated the SQL-database, you'll have to reindex records with opensearch",
        fg="red",
    )


if __name__ == "__main__":
    # gets executed when file is called directly, but not when imported
    execute_upgrade()
