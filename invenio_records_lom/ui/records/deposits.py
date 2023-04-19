# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2023 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""View-functions for deposit-related pages."""

from flask import current_app, g, render_template
from flask_login import current_user, login_required
from invenio_i18n.ext import current_i18n
from invenio_records_resources.services.files.results import FileList
from invenio_records_resources.services.records.results import RecordItem
from invenio_users_resources.proxies import current_user_resources

from ...proxies import current_records_lom
from ...utils import LOMMetadata, get_oefosdict
from .decorators import pass_draft, pass_draft_files


def get_deposit_template_context(**extra_form_config_kwargs) -> dict:
    """Get context for deposit-template from db, current_app.config."""
    app_config = current_app.config
    locale = str(current_i18n.locale)
    locale = locale if locale in ["de", "en"] else "en"

    oefos_dict = get_oefosdict("en")
    oefos_vocabulary = {
        num: {"name": f"{num} - {name}", "value": name}
        for num, name in oefos_dict.items()
    }
    # TODO: dont hardcode vocabularies here...
    license_vocabulary = {
        "https://creativecommons.org/licenses/by/4.0": {
            "name": "CC BY 4.0 - Creative Commons Attribution 4.0 International",
        },
        "https://creativecommons.org/licenses/by-nc/4.0": {
            "name": "CC BY-NC 4.0 - Creative Commons Attribution Non-Commercial 4.0 International",
        },
        "https://creativecommons.org/licenses/by-nc-nd/4.0": {
            "name": "CC BY-NC-ND 4.0 - Creative Commons Attribution Non-Commercial No-Derivatives 4.0 International",
        },
        "https://creativecommons.org/licenses/by-nc-sa/4.0": {
            "name": "CC BY-NC-SA 4.0 - Creative Commons Attribution Non-Commercial Share-Alike 4.0 International",
        },
        "https://creativecommons.org/licenses/by-nd/4.0": {
            "name": "CC BY-ND 4.0 - Creative Commons Attribution No-Derivatives 4.0 International",
        },
        "https://creativecommons.org/licenses/by-sa/4.0": {
            "name": "CC BY-SA 4.0 - Creative Commons Attribution Share-Alike 4.0 International",
        },
    }
    contributor_vocabulary = {
        "Author": {"name": "Author"},
        "Publisher": {"name": "Publisher"},
    }
    language_vocabulary = {"de": {"name": "Deutsch"}, "en": {"name": "English"}}
    resourcetype_vocabulary = {"": {"name": ""}, "video": {"name": "Video"}}

    return {
        "files": {"default_preview": None, "entries": [], "links": {}},
        "forms_config": {
            "autocomplete_names": "search",
            "current_locale": str(current_i18n.locale),
            "decimal_size_display": app_config.get(
                "APP_RDM_DISPLAY_DECIMAL_FILE_SIZES", True
            ),
            "default_locale": app_config.get("BABEL_DEFAULT_LOCALE", "en"),
            "links": {},  # TODO
            "pids": [],  # TODO
            "quota": app_config.get("APP_RDM_DEPOSIT_FORM_QUOTA"),
            "vocabularies": {
                "contributor": contributor_vocabulary,
                "language": language_vocabulary,
                "license": license_vocabulary,
                "oefos": oefos_vocabulary,
                "resourcetype": resourcetype_vocabulary,
            },
            **extra_form_config_kwargs,
        },
        # can't get the following from `app_config`, as that ignores blueprint-prefix...
        "searchbar_config": {"searchUrl": "/lom/search"},
    }


@login_required
def deposit_create() -> str:
    """Create a new deposit."""
    service_config = current_records_lom.records_service.config

    pids = {}
    if "doi" in service_config.pids_providers:
        pids = {"doi": {"provider": "external", "identifier": ""}}
    empty_metadata: LOMMetadata = LOMMetadata.create(
        resource_type="upload",
        pids=pids,
    )
    empty_metadata.record["status"] = "draft"
    defaults = current_app.config.get("LOM_DEPOSIT_FORM_DEFAULTS", {})
    for dotted_key, value in defaults.items():
        empty_metadata.record.setdefault(dotted_key, value)

    template_context: dict = get_deposit_template_context(createUrl="/api/lom")
    return render_template(
        "invenio_records_lom/records/deposit.html",
        files=template_context["files"],
        forms_config=template_context["forms_config"],
        # preselectedCommunity=?,
        record=empty_metadata.json,
        searchbar_config=template_context["searchbar_config"],
    )


@login_required
@pass_draft(expand=True)
@pass_draft_files
def deposit_edit(
    pid_value: str, draft: RecordItem = None, draft_files: FileList = None
) -> str:
    """Edit an existing deposit."""
    files_dict = None if draft_files is None else draft_files.to_dict()
    record = draft.to_dict()

    template_context = get_deposit_template_context(
        createUrl=f"/api/lom/records/{pid_value}/draft"
    )
    return render_template(
        "invenio_records_lom/records/deposit.html",
        files=files_dict,
        forms_config=template_context["forms_config"],
        permissions=draft.has_permissions_to(["new_version", "delete_draft"]),
        record=record,
        searchbar_config=template_context["searchbar_config"],
    )


@login_required
def uploads():
    """Show overview of lom-records uploaded by user, upload further records."""
    avatar_url = current_user_resources.users_service.links_item_tpl.expand(
        g.identity, current_user
    )["avatar"]
    return render_template(
        "invenio_records_lom/uploads.html",
        # TODO: newer versions of the original template now also take `searchbar_config` here
        # see `invenio_app_rdm/users_ui/views/dashboard.py:uploads`
        # also see `invenio_app_rdm/users_ui/templates/uploads.html`
        # searchbar_config={"searchUrl": ...},
        user_avatar=avatar_url,
    )
