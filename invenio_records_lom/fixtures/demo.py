# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2024 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Fake LOM demo records."""

import json
from functools import partial
from io import BytesIO

from faker import Faker
from flask import current_app
from invenio_access.permissions import system_identity
from invenio_records_resources.services.records.results import RecordItem

from ..proxies import current_records_lom
from .tasks import create_lom_record


#
# functions for LOM datatypes
#
def langstringify(fake: Faker, text: str, lang: str = "") -> dict:
    """Wrap `text` in a dict, emulating LOMv1.0 langstring-objects.

    If `lang` is given and None, no "lang"-key is added to the returned dict.
    If `lang` is given and truthy, its value is used for the "lang"-key.
    If `lang` is not given or is falsy but not None, a fake-value is used for "lang".
    """
    langstring = {}
    if lang is not None:
        langstring["lang"] = lang or create_fake_language(fake)
    langstring["#text"] = text
    return {"langstring": langstring}


def vocabularify(fake: Faker, choices: list) -> dict:
    """Emulate LOMv1.0 Vocabulary-objects.

    Randomly draw a choice from `choices`, then wrap it in a dict.
    """
    return {
        "source": langstringify(fake, "LOMv1.0", lang="x-none"),
        "value": langstringify(fake, fake.random.choice(choices), lang="x-none"),
    }


def create_fake_datetime(fake: Faker) -> dict:
    """Create a fake datetime dict, as per LOMv1.0 Datetime-object-specification."""
    pattern = fake.random.choice(["YMDhmsTZD", "YMDhms", "YMD"])

    if pattern == "YMD":
        datetime = fake.date()
    elif pattern == "YMDhms":
        datetime = fake.date_time().isoformat()
    elif pattern == "YMDhmsTZD":
        time_zone_designator = fake.pytimezone()
        datetime = fake.date_time(tzinfo=time_zone_designator).isoformat()
    else:
        datetime = "1970"

    return {"datetime": datetime, "description": langstringify(fake, fake.sentence())}


def create_fake_duration(fake: Faker) -> dict:
    """Create a fake duration dict, as per LOM-UIBK specification."""
    randint = fake.random.randint
    return {
        "datetime": f"{randint(0,23):02}:{randint(0,59):02}:{randint(0,59):02}",
        "description": langstringify(fake, fake.sentence()),
    }


def create_fake_vcard(fake: Faker) -> str:
    """Return a placeholder-string for a vcard-object."""
    return f"{fake.last_name()}, {fake.first_name()}"


#
# functions for elements that are part of more than one category
#
def create_fake_language(fake: Faker) -> str:
    """Create a fake language-code, as required for "language"-keys by LOMv1.0."""
    language_codes = [
        "EN",
        "en-us",
        "eng",
        "eng-US",
    ]
    return fake.random.choice(language_codes)


def create_fake_identifier(fake: Faker) -> dict:
    """Create a fake "identifier"-element, compatible with LOMv1.0."""
    catalog = fake.random.choice(["URL", "ISBN"])
    entry = fake.uri() if catalog == "URL" else fake.isbn13()
    lang = fake.random.choice([None, create_fake_language(fake)])

    return {
        "catalog": catalog,
        "entry": langstringify(fake, entry, lang=lang),
    }


def create_fake_contribute(fake: Faker, roles: list) -> dict:
    """Create a fake "contribute"-element, compatible with LOMv1.0."""
    return {
        "role": vocabularify(fake, roles),
        "entity": [create_fake_vcard(fake) for __ in range(2)],
        "date": create_fake_datetime(fake),
    }


#
# functions for categories or used by only one category
#
def create_fake_general(fake: Faker) -> dict:
    """Create a fake "general"-element, compatible with LOMv1.0."""
    structures = ["atomic", "collection", "networked", "hierarchical", "linear"]
    aggregationlevels = ["1", "2", "3", "4"]

    return {
        "identifier": [create_fake_identifier(fake) for __ in range(2)],
        "title": langstringify(fake, " ".join(fake.words()).title()),
        "language": [fake.random.choice([create_fake_language(fake), "none"])],
        "description": [langstringify(fake, fake.paragraph()) for __ in range(2)],
        "keyword": [langstringify(fake, fake.word()) for __ in range(2)],
        "coverage": [langstringify(fake, fake.paragraph()) for __ in range(2)],
        "structure": vocabularify(fake, structures),
        "aggregationlevel": vocabularify(fake, aggregationlevels),
    }


def create_fake_lifecycle(fake: Faker) -> dict:
    """Create a fake "lifecycle"-element, compatible with LOMv1.0."""
    roles = [
        "author",
        "publisher",
        "unknown",
        "initiator",
        "terminator",
        "validator",
        "editor",
        "graphical designer",
        "technical implementer",
        "content provider",
        "technical validator",
        "educational validator",
        "script writer",
        "instructional designer",
        "subject matter expert",
    ]

    statuses = ["draft", "final", "revised", "unavailable"]

    randint = fake.random.randint

    return {
        "version": langstringify(fake, f"{randint(0,9)}.{randint(0,9)}"),
        "status": vocabularify(fake, statuses),
        "contribute": [
            create_fake_contribute(fake, ["author"]),  # guarantee one author exists
            create_fake_contribute(fake, roles[1:]),  # create one random other role
        ],
    }


def create_fake_metametadata(fake: Faker) -> dict:
    """Create a fake "metametadata"-element, compatible with LOMv1.0."""
    roles = ["creator", "validator"]
    return {
        "identifier": [create_fake_identifier(fake) for __ in range(2)],
        "contribute": [create_fake_contribute(fake, roles) for __ in range(2)],
        "metadataschemas": ["LOMv1.0"],
        "language": create_fake_language(fake),
    }


def create_fake_technical(fake: Faker) -> dict:
    """Create a fake "technical"-element, with fields from LOMv1.0 and LOM-UIBK."""
    return {
        "format": [fake.random.choice([fake.mime_type(), "non-digital"])],
        "size": str(fake.random.randint(1, 2**32)),
        "location": {"type": "URI", "#text": fake.uri()},
        "thumbnail": {"url": fake.uri()},
        "requirement": [create_fake_requirement(fake) for __ in range(2)],
        "installationremarks": langstringify(fake, fake.paragraph()),
        "otherplatformrequirements": langstringify(fake, fake.paragraph()),
        "duration": create_fake_duration(fake),
    }


def create_fake_requirement(fake: Faker) -> dict:
    """Create a fake "requirement"-element, compatible with LOMv1.0."""
    return {
        "orcomposite": [create_fake_orcomposite(fake) for __ in range(2)],
    }


def create_fake_orcomposite(fake: Faker) -> dict:
    """Create a fake "orcomposite"-element, compatible with LOMv1.0."""
    type_ = fake.random.choice(["operating system", "browser"])
    if type_ == "operating system":
        requirement_names = [
            "pc-dos",
            "ms-windows",
            "macos",
            "unix",
            "multi-os",
            "none",
        ]
    else:
        requirement_names = [
            "any",
            "netscape communicator",
            "ms-internet explorer",
            "opera",
            "amaya",
        ]

    return {
        "type": vocabularify(fake, [type_]),
        "name": vocabularify(fake, requirement_names),
        "minimumversion": str(fake.random.randint(1, 4)),
        "maximumversion": str(fake.random.randint(5, 8)),
    }


def create_fake_educational(fake: Faker) -> dict:
    """Create a fake "educational"-element, compatible with LOMv1.0."""
    interactivity_types = ["active", "expositive", "mixed"]
    levels = ["very low", "low", "medium", "high", "very high"]
    difficulties = ["very easy", "easy", "medium", "difficult", "very difficult"]
    end_user_roles = ["teacher", "author", "learner", "manager"]
    contexts = ["school", "higher education", "training", "other"]

    random_int = fake.random.randint

    return {
        "interactivitytype": vocabularify(fake, interactivity_types),
        "learningresourcetype": create_fake_learningresourcetype(fake),
        "interactivitylevel": vocabularify(fake, levels),
        "semanticdensity": vocabularify(fake, levels),
        "intendedenduserrole": vocabularify(fake, end_user_roles),
        "context": [vocabularify(fake, contexts) for __ in range(2)],
        "typicalagerange": langstringify(fake, f"{random_int(1,4)}-{random_int(5,9)}"),
        "difficulty": vocabularify(fake, difficulties),
        "typicallearningtime": create_fake_duration(fake),
        "description": langstringify(fake, fake.paragraph()),
        "language": [create_fake_language(fake) for __ in range(2)],
    }


def create_fake_learningresourcetype(fake: Faker) -> dict:
    """Create a fake "learningresourcetype"-element, compatible with LOM-UIBK."""
    url_endings = [
        "application",
        "assessment",
        "audio",
        "case_study",
        "course",
        "data",
        "diagram",
        "drill_and_practice",
        "educational_game",
        "experiment",
        "image",
        "index",
        "lesson_plan",
        "map",
        "portal",
        "questionnaire",
        "script",
        "sheet_music",
        "simulation",
        "slide",
        "text",
        "textbook",
        "video",
        "web_page",
        "worksheet",
        "other",
    ]
    urls = [f"https://w3id.org/kim/hcrt/{end}" for end in url_endings]
    source_url = "https://w3id.org/kim/hcrt/scheme"
    return {
        "source": langstringify(fake, source_url, lang="x-none"),
        "id": fake.random.choice(urls),
        "entry": langstringify(fake, fake.word()),
    }


def create_fake_rights(fake: Faker) -> dict:
    """Create a fake "rights"-element, compatible with LOMv1.0."""
    urls = [
        "https://creativecommons.org/publicdomain/zero/1.0/",
        "https://creativecommons.org/licenses/by/4.0",
        "https://creativecommons.org/licenses/by-sa/4.0",
        "https://creativecommons.org/licenses/by-nd/4.0",
        "https://creativecommons.org/licenses/by-nc/4.0",
        "https://creativecommons.org/licenses/by-nc-sa/4.0",
        "https://creativecommons.org/licenses/by-nc-nd/4.0",
        "https://mit-license.org/",
    ]
    url = fake.random.choice(urls)
    lang = "x-t-cc-url" if url.startswith("https://creativecommons.org/") else None
    return {
        "cost": vocabularify(fake, ["yes", "no"]),
        "copyrightandotherrestrictions": vocabularify(fake, ["yes", "no"]),
        "description": langstringify(fake, fake.paragraph(), lang=lang),
        "url": fake.random.choice(urls),
    }


def create_fake_relation(fake: Faker) -> dict:
    """Create a fake "relation"-element, compatible with LOMv1.0."""
    kinds = [
        "ispartof",
        "haspart",
        "isversionof",
        "hasversion",
        "isformatof",
        "hasformat",
        "references",
        "isreferencedby",
        "isbasedon",
        "isbasisfor",
        "requires",
        "isrequiredby",
    ]

    return {
        "kind": vocabularify(fake, kinds),
        "resource": {
            "identifier": [create_fake_identifier(fake) for __ in range(2)],
            "description": [langstringify(fake, fake.paragraph()) for __ in range(2)],
        },
    }


def create_fake_annotation(fake: Faker) -> dict:
    """Create a fake "annotation"-element, compatible with LOMv1.0."""
    return {
        "entity": create_fake_vcard(fake),
        "date": create_fake_datetime(fake),
        "description": langstringify(fake, fake.paragraph()),
    }


def create_fake_classification(fake: Faker) -> dict:
    """Create a fake "classification"-element, compatible with LOMv1.0."""
    purposes = [
        "discipline",
        "idea",
        "prerequisite",
        "educational objective",
        "accessability restrictions",
        "educational level",
        "skill level",
        "security level",
        "competency",
    ]

    return {
        "purpose": vocabularify(fake, purposes),
        "taxonpath": [create_fake_taxonpath(fake) for __ in range(2)],
        "description": langstringify(fake, fake.paragraph()),
        "keyword": langstringify(fake, fake.word()),
    }


def create_fake_taxonpath(fake: Faker) -> dict:
    """Create a fake "taxonpath"-element, compatible with LOMv1.0."""
    return {
        "source": langstringify(fake, fake.word(), lang="x-none"),
        "taxon": [create_fake_taxon(fake) for __ in range(2)],
    }


def create_fake_taxon(fake: Faker) -> dict:
    """Create a fake "taxon"-element, compatible with LOMv1.0."""
    lang = fake.random.choice([None, create_fake_language(fake)])
    return {
        "id": fake.lexify(
            "?????",
            letters="ABCDEFGHIJKLMNOPQRSTUVWXYZ.0123456789",
        ),
        "entry": langstringify(fake, fake.word(), lang=lang),
    }


#
# functions for creating LOMv1.0-fakes
#
def create_fake_metadata(fake: Faker) -> dict:
    """Create a fake json-representation of a "lom"-element, compatible with LOMv1.0."""
    data_to_use = {
        "general": create_fake_general(fake),
        "lifecycle": create_fake_lifecycle(fake),
        "metametadata": create_fake_metametadata(fake),
        "technical": create_fake_technical(fake),
        "educational": create_fake_educational(fake),
        "rights": create_fake_rights(fake),
        "relation": [create_fake_relation(fake) for __ in range(2)],
        "annotation": [create_fake_annotation(fake) for __ in range(2)],
        "classification": [create_fake_classification(fake) for __ in range(2)],
    }

    return json.loads(json.dumps(data_to_use))


def create_fake_access(fake: Faker) -> dict:
    """Create a fake json of an "access"-element, compatible with invenio."""
    fake_access_type = fake.random.choice(["public", "restricted"])

    has_embargo = fake.boolean()
    if has_embargo:
        fake_embargo = {
            "until": fake.future_date(end_date="+365d").isoformat(),
            "reason": "Fake embargo for fake record.",
            "active": True,
        }
    else:
        fake_embargo = {}

    return {
        "files": fake_access_type,
        "record": fake_access_type,
        "embargo": fake_embargo,
    }


def create_fake_data(
    fake: Faker,
    resource_type: str,
    *,
    files_enabled: bool = False,
) -> dict:
    """Create a fake json of an invenio-record, "metadata" conforms to LOM-standard."""
    resource_types = current_app.config["LOM_RESOURCE_TYPES"]
    resource_type = resource_type or fake.random.choice(resource_types)
    return {
        # these values get processed by service.config.components
        "access": create_fake_access(fake),
        "files": {"enabled": files_enabled},
        "metadata": create_fake_metadata(fake),
        "pids": {},
        "resource_type": resource_type,
    }


#
# helpers for `publish_fake_record`
#
def attach_fake_files(fake: Faker, draft_item: RecordItem) -> None:
    """Attach fake files to the record behind `draft_item`."""
    service = current_records_lom.records_service
    df_service = service.draft_files

    # partially apply identity=system_identity
    update_draft = partial(service.update_draft, identity=system_identity)
    commit_file = partial(df_service.commit_file, identity=system_identity)
    init_files = partial(df_service.init_files, identity=system_identity)
    set_file_content = partial(df_service.set_file_content, identity=system_identity)

    # create and attach fake files
    fake_files = {
        fake.file_name(extension="txt"): fake.sentence().encode() for __ in range(2)
    }

    init_files(id_=draft_item.id, data=[{"key": name} for name in fake_files])
    for file_name, file_content in fake_files.items():
        stream = BytesIO(file_content)
        set_file_content(id_=draft_item.id, file_key=file_name, stream=stream)
        commit_file(id_=draft_item.id, file_key=file_name)

    draft_data = draft_item.to_dict()
    draft_data["files"]["default_preview"] = next(iter(fake_files))
    draft_item = update_draft(id_=draft_item.id, data=draft_data)


def create_then_publish(
    fake: Faker,
    data: dict,
    *,
    create_fake_files: bool = False,
) -> RecordItem:
    """Create a fake record, then publish it.

    if `create_fake_files` is True, attach fake files to created fake record.
    """
    service = current_records_lom.records_service

    # create
    draft_item = service.create(data=data, identity=system_identity)

    if create_fake_files:
        attach_fake_files(fake, draft_item)

    return service.publish(id_=draft_item.id, identity=system_identity)


def inject_relation(data: dict, kind: str, pid: str) -> None:
    """Inject relation of kind `kind` into `data` under entry `pid`.

    `data` is a json-representation of data, compatible with LOMv1.0.
    `kind` is a kind, as in LOMv1.0's `relation`-group.
    `pid` is entry, as in LOMv1.0's `relation.resource.identifier` category.
    """
    kind = {
        "source": langstringify(None, "LOMv1.0", lang="x-none"),
        "value": langstringify(None, kind, lang="x-none"),
    }
    identifier = {"catalog": "repo-pid", "entry": langstringify(None, pid, lang=None)}
    resource = {"identifier": [identifier]}
    data["metadata"]["relation"].append({"kind": kind, "resource": resource})


def link_up(whole_id: str, part_id: str) -> None:
    """Links up the records behind `whole_id` and `part_id`.

    `whole_record`'s json gains a new "haspart"-relation to `part_record`.
    `part_record`'s json gains a new "ispartof"-relation to `whole_record`.
    Relations are encoded according LOMv1.0's `relation`-category.
    """
    service = current_records_lom.records_service

    # partially apply identity=system_identity
    edit = partial(service.edit, identity=system_identity)
    publish = partial(service.publish, identity=system_identity)
    update_draft = partial(service.update_draft, identity=system_identity)

    # add "haspart"-relation to `whole_record`
    whole_draft_item = edit(id_=whole_id)
    whole_data = whole_draft_item.to_dict()
    inject_relation(whole_data, "haspart", part_id)
    updated_whole_draft_item = update_draft(id_=whole_id, data=whole_data)
    publish(id_=updated_whole_draft_item.id)

    # add "ispartof"-relation to `part_record`
    part_draft_item = edit(id_=part_id)
    part_data = part_draft_item.to_dict()
    inject_relation(part_data, "ispartof", whole_id)
    updated_part_draft_item = update_draft(id_=part_id, data=part_data)
    publish(id_=updated_part_draft_item.id)


#
# functions for publishing fake records
#
def publish_fake_record(fake: Faker) -> None:
    """Enter fake records into the SQL-database."""
    file_data = create_fake_data(fake, resource_type="file", files_enabled=True)
    create_then_publish(fake=fake, data=file_data, create_fake_files=True)


def publish_fake_record_over_celery(fake: Faker) -> None:
    """Create fake records via celery."""
    data = create_fake_data(fake, resource_type="file", files_enabled=False)
    create_lom_record.delay(data)


def publish_fake_records(number: int, seed: int = 42) -> list:
    """Create `number` jsons adhering to LOM-standard, using `seed` as RNG-seed."""
    fake = Faker()
    Faker.seed(seed)

    return [publish_fake_record(fake) for __ in range(number)]
