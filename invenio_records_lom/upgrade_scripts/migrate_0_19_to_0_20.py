# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Record migration script from invenio-records-lom v0.19 to v0.20.

To upgrade, call the whole file from within app-context.
(e.g. via `pipenv run invenio shell \
           /path/to/invenio_records_lom/upgrade_scripts/migrate_0_19_to_0_20.py`)
(e.g. via `pipenv run invenio shell \
           $(find $(pipenv --venv)/lib/*/site-packages/invenio_records_lom \
           -name migrate_0_19_to_0_20.py))`)
"""

from copy import deepcopy

from click import secho
from invenio_db import db
from invenio_i18n import gettext as _

from invenio_records_lom.records.api import LOMDraft, LOMRecord


def execute_upgrade() -> None:  # noqa: C901
    """Exceute upgrade from `invenio-records-lom` `v0.19` to `v0.20`."""
    secho(
        "LOM upgrade: ensuring `metadata.rights` has correct `name` property",
        fg="green",
    )

    def get_new_json(old_json: dict) -> dict | None:
        """Get updated json from current json.

        if update is necessary, return updated JSON
        otherwise, return `None`
        """
        license_vocabulary = {
            "https://creativecommons.org/publicdomain/zero/1.0/": {
                "name": "CC0 1.0 - Creative Commons CC0 1.0 Universal",
            },
            "https://creativecommons.org/licenses/by/4.0/": {
                "name": _("CC BY 4.0 - Creative Commons Attribution 4.0 International"),
            },
            "https://creativecommons.org/licenses/by-nc/4.0/": {
                "name": _(
                    "CC BY-NC 4.0 - Creative Commons Attribution Non-Commercial 4.0 International",
                ),
            },
            "https://creativecommons.org/licenses/by-nc-nd/4.0/": {
                "name": _(
                    "CC BY-NC-ND 4.0 - Creative Commons Attribution Non-Commercial No-Derivatives 4.0 International",
                ),
            },
            "https://creativecommons.org/licenses/by-nc-sa/4.0/": {
                "name": _(
                    "CC BY-NC-SA 4.0 - Creative Commons Attribution Non-Commercial Share-Alike 4.0 International",
                ),
            },
            "https://creativecommons.org/licenses/by-nd/4.0/": {
                "name": _(
                    "CC BY-ND 4.0 - Creative Commons Attribution No-Derivatives 4.0 International",
                ),
            },
            "https://creativecommons.org/licenses/by-sa/4.0/": {
                "name": _(
                    "CC BY-SA 4.0 - Creative Commons Attribution Share-Alike 4.0 International",
                ),
            },
            # some seem 2 times, but this is because the lack of final slash character ("/") - demo data from v0.19
            "https://creativecommons.org/licenses/by/4.0": {
                "name": _("CC BY 4.0 - Creative Commons Attribution 4.0 International"),
            },
            "https://creativecommons.org/licenses/by-nc/4.0": {
                "name": _(
                    "CC BY-NC 4.0 - Creative Commons Attribution Non-Commercial 4.0 International",
                ),
            },
            "https://creativecommons.org/licenses/by-nc-nd/4.0": {
                "name": _(
                    "CC BY-NC-ND 4.0 - Creative Commons Attribution Non-Commercial No-Derivatives 4.0 International",
                ),
            },
            "https://creativecommons.org/licenses/by-nc-sa/4.0": {
                "name": _(
                    "CC BY-NC-SA 4.0 - Creative Commons Attribution Non-Commercial Share-Alike 4.0 International",
                ),
            },
            "https://creativecommons.org/licenses/by-nd/4.0": {
                "name": _(
                    "CC BY-ND 4.0 - Creative Commons Attribution No-Derivatives 4.0 International",
                ),
            },
            "https://creativecommons.org/licenses/by-sa/4.0": {
                "name": _(
                    "CC BY-SA 4.0 - Creative Commons Attribution Share-Alike 4.0 International",
                ),
            },
            "https://mit-license.org/": {"name": _("MIT License")},
        }

        property_to_add = "name"
        current_rights = old_json.get("metadata", {}).get("rights", {})
        if current_rights is None:
            # no rights - nothing to update
            return None
        if property_to_add in current_rights:
            # property already there - no need to update
            return None

        # add title from license vocabulary
        new_json = deepcopy(old_json)
        try:
            new_json["metadata"]["rights"]["name"] = license_vocabulary[
                old_json["metadata"]["rights"]["url"]
            ]["name"]
        except KeyError:
            new_json["metadata"]["rights"]["name"] = "Other"

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
        "Successfully added `name` to `metadata.rights` where necessary!",
        fg="green",
    )
    secho(
        "NOTE: this only updated the SQL-database, you'll have to reindex records with opensearch",
        fg="red",
    )


if __name__ == "__main__":
    # gets executed when file is called directly, but not when imported
    execute_upgrade()
