# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 Graz University of Technology.
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
from ...utils import DotAccessWrapper, LOMRecordData, get_oefosdict
from .decorators import (
    pass_draft,
    pass_draft_files,
    pass_is_oer_certified,
    require_lom_permission,
)


def get_deposit_template_context(**extra_form_config_kwargs: dict) -> dict:
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
        "https://creativecommons.org/publicdomain/zero/1.0/": {
            "name": "CC0 1.0 - Creative Commons CC0 1.0 Universal",
        },
        "https://creativecommons.org/licenses/by/4.0/": {
            "name": "CC BY 4.0 - Creative Commons Attribution 4.0 International",
        },
        "https://creativecommons.org/licenses/by-nc/4.0/": {
            "name": "CC BY-NC 4.0 - Creative Commons Attribution Non-Commercial 4.0 International",
        },
        "https://creativecommons.org/licenses/by-nc-nd/4.0/": {
            "name": "CC BY-NC-ND 4.0 - Creative Commons Attribution Non-Commercial No-Derivatives 4.0 International",
        },
        "https://creativecommons.org/licenses/by-nc-sa/4.0/": {
            "name": "CC BY-NC-SA 4.0 - Creative Commons Attribution Non-Commercial Share-Alike 4.0 International",
        },
        "https://creativecommons.org/licenses/by-nd/4.0/": {
            "name": "CC BY-ND 4.0 - Creative Commons Attribution No-Derivatives 4.0 International",
        },
        "https://creativecommons.org/licenses/by-sa/4.0/": {
            "name": "CC BY-SA 4.0 - Creative Commons Attribution Share-Alike 4.0 International",
        },
    }
    contributor_vocabulary = {
        "Author": {"name": "Author"},
        "Publisher": {"name": "Publisher"},
    }
    format_vocabulary = {
        "application/epub+zip": {
            "name": "application/epub+zip - Electronic Publication (.epub)",
        },
        "application/gzip": {
            "name": "application/gzip - GZip Compressed Archive (.gz)",
        },
        "application/json": {"name": "application/json - JSON format (.json)"},
        "application/msword": {"name": "application/msword - Microsoft Word (.doc)"},
        "application/octet-stream": {
            "name": "application/octet-stream - Other Binary Documents",
        },
        "application/pdf": {
            "name": "application/pdf - Adobe Portable Document Format (.pdf)",
        },
        "application/vnd.ms-excel": {
            "name": "application/vnd.ms-excel - Microsoft Excel (.xls)",
        },
        "application/vnd.ms-powerpoint": {
            "name": "application/vnd.ms-powerpoint - Microsoft PowerPoint (.ppt)",
        },
        "application/xml": {"name": "application/xml - XML (.xml)"},
        "application/zip": {"name": "application/zip - ZIP Archive (.zip)"},
        "audio/aac": {"name": "audio/aac - AAC Audio (.aac)"},
        "audio/midi": {
            "name": "audio/midi - Musical Instrument Digital Interface (.midi, .mid)",
        },
        "audio/mpeg": {"name": "audio/mpeg - MP3 Audio (.mp3)"},
        "audio/wav": {"name": "audio/wav - Waveform Audio Format (.wav)"},
        "image/bmp": {"name": "image/bmp - Windows OS/2 Bitmap Graphics (.bmp)"},
        "image/gif": {"name": "image/gif - Graphics Interchange Format (.gif)"},
        "image/jpeg": {"name": "image/jpeg - JPEG images (.jpg, .jpeg)"},
        "image/png": {"name": "image/png - Portable Network Graphics (.png)"},
        "image/svg+xml": {"name": "image/svg+xml - Scalable Vector Graphics (.svg)"},
        "image/tiff": {"name": "image/tiff - Tagged Image File Format (.tif, .tiff)"},
        "image/webp": {"name": "image/webp - WEBP Image (.webp)"},
        "text/css": {"name": "text/css - Cascading Style Sheets (.css)"},
        "text/csv": {"name": "text/csv - Comma-separated values (.csv)"},
        "text/html": {"name": "text/html - HyperText Markup Language (.html)"},
        "text/plain": {"name": "text/plain - Other Text, ASCII (.txt, …)"},
        "video/mp4": {"name": "video/mp4 - MP4 Video (.mp4)"},
        "video/x-msvideo": {"name": "video/x-msvideo - Audio Video Interleave (.avi)"},
    }

    language_vocabulary = {"de": {"name": "Deutsch"}, "en": {"name": "English"}}
    resourcetype_vocabulary = {
        "https://w3id.org/kim/hcrt/application": {"name": "Software Application"},
        "https://w3id.org/kim/hcrt/assessment": {"name": "Assessment"},
        "https://w3id.org/kim/hcrt/audio": {"name": "Audio Recording"},
        "https://w3id.org/kim/hcrt/case_study": {"name": "Case Study"},
        "https://w3id.org/kim/hcrt/course": {"name": "Course"},
        "https://w3id.org/kim/hcrt/data": {"name": "Data"},
        "https://w3id.org/kim/hcrt/diagram": {"name": "Diagram"},
        "https://w3id.org/kim/hcrt/drill_and_practice": {"name": "Drill and Practice"},
        "https://w3id.org/kim/hcrt/educational_game": {"name": "Game"},
        "https://w3id.org/kim/hcrt/experiment": {"name": "Experiment"},
        "https://w3id.org/kim/hcrt/image": {"name": "Image"},
        "https://w3id.org/kim/hcrt/index": {"name": "Reference Work"},
        "https://w3id.org/kim/hcrt/lesson_plan": {"name": "Lesson Plan"},
        "https://w3id.org/kim/hcrt/map": {"name": "Map"},
        "https://w3id.org/kim/hcrt/portal": {"name": "Web Portal"},
        "https://w3id.org/kim/hcrt/questionnaire": {"name": "Questionnaire"},
        "https://w3id.org/kim/hcrt/script": {"name": "Script"},
        "https://w3id.org/kim/hcrt/sheet_music": {"name": "Sheet Music"},
        "https://w3id.org/kim/hcrt/simulation": {"name": "Simulation"},
        "https://w3id.org/kim/hcrt/slide": {"name": "Presentation"},
        "https://w3id.org/kim/hcrt/text": {"name": "Text"},
        "https://w3id.org/kim/hcrt/textbook": {"name": "Textbook"},
        "https://w3id.org/kim/hcrt/video": {"name": "Video"},
        "https://w3id.org/kim/hcrt/web_page": {"name": "Web Page"},
        "https://w3id.org/kim/hcrt/worksheet": {"name": "Worksheet"},
        "https://w3id.org/kim/hcrt/other": {"name": "Other"},
    }
    # sort `resourcetype_vocabulary` by name
    resourcetype_vocabulary = dict(
        sorted(resourcetype_vocabulary.items(), key=lambda item: item[1]["name"]),
    )

    return {
        "files": {"default_preview": None, "entries": [], "links": {}},
        "forms_config": {
            "autocomplete_names": "search",
            "current_locale": str(current_i18n.locale),
            "decimal_size_display": app_config.get(
                "APP_RDM_DISPLAY_DECIMAL_FILE_SIZES",
                True,
            ),
            "default_locale": app_config.get("BABEL_DEFAULT_LOCALE", "en"),
            "links": {},
            "pids": [],
            "quota": app_config.get("APP_RDM_DEPOSIT_FORM_QUOTA"),
            "vocabularies": {
                "contributor": contributor_vocabulary,
                "format": format_vocabulary,
                "language": language_vocabulary,
                "license": license_vocabulary,
                "oefos": oefos_vocabulary,
                "resourcetype": resourcetype_vocabulary,
            },
            **extra_form_config_kwargs,
        },
        # can't get the following from `app_config`, as that ignores blueprint-prefix...
        "searchbar_config": {"searchUrl": "/oer/search"},
    }


@login_required
@require_lom_permission("create", default_endpoint="invenio_records_lom.uploads")
def deposit_create() -> str:
    """Create a new deposit."""
    service_config = current_records_lom.records_service.config

    pids = {}
    if "doi" in service_config.pids_providers:
        pids = {"doi": {"provider": "external", "identifier": ""}}
    empty_record: LOMRecordData = LOMRecordData.create(
        resource_type="upload",
        pids=pids,
    )
    empty_record["status"] = "draft"

    # insert default-publisher from config (if exists)
    app_config = current_app.config
    if default_publisher := app_config.get("LOM_PUBLISHER"):
        empty_record.metadata.append_contribute(default_publisher, role="publisher")

    # update json with defaults
    defaults = current_app.config.get("LOM_DEPOSIT_FORM_DEFAULTS", {})
    record_json = empty_record.json
    record_dot_access = DotAccessWrapper(record_json)
    for dotted_key, value in defaults.items():
        record_dot_access.setdefault(dotted_key, value)

    template_context: dict = get_deposit_template_context(createUrl="/api/oer")
    return render_template(
        "invenio_records_lom/records/deposit.html",
        files=template_context["files"],
        forms_config=template_context["forms_config"],
        # preselectedCommunity=?,
        record=record_json,
        searchbar_config=template_context["searchbar_config"],
    )


@login_required
@require_lom_permission("handle_oer", default_endpoint="invenio_records_lom.uploads")
@pass_draft(expand=True)
@pass_draft_files
def deposit_edit(
    pid_value: str,
    draft: RecordItem = None,
    draft_files: FileList = None,
) -> str:
    """Edit an existing deposit."""
    files_dict = None if draft_files is None else draft_files.to_dict()
    record = draft.to_dict()

    template_context = get_deposit_template_context(
        createUrl=f"/api/oer/records/{pid_value}/draft",
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
@pass_is_oer_certified
def uploads(*, is_oer_certified: bool = False) -> str:
    """Show overview of lom-records uploaded by user, upload further records."""
    avatar_url = current_user_resources.users_service.links_item_tpl.expand(
        g.identity,
        current_user,
    )["avatar"]

    if is_oer_certified:
        template = "invenio_records_lom/uploads.html"
    else:
        template = "invenio_records_lom/not_licensed_text.html"

    return render_template(
        template,
        # TODO: newer versions of the original template now also take `searchbar_config`
        # here
        # see `invenio_app_rdm/users_ui/views/dashboard.py:uploads`
        # also see `invenio_app_rdm/users_ui/templates/uploads.html`
        # searchbar_config={"searchUrl": ...}, #noqa: ERA001
        user_avatar=avatar_url,
    )
