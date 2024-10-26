..
    Copyright (C) 2020 Graz University of Technology.

    invenio-records-lom is free software; you can redistribute it and/or modify it
    under the terms of the MIT License; see LICENSE file for more details.

Changes
=======

Version v0.17.0 (release 2024-10-26)

- jinja: use invenio's file_list macro over our copy
- ui: add button for downloading all files
- ui: implement collapsing for file-preview/file-list
- ui: add `technical_metadata` side-card
- ui: align `<EditButton />`'s style with invenio's
- ui: add info-link to stats sidecard
- ui: align side-cards' style with invenio's
- ui: align record-labels' style with invenio's
- ui: remove `dx.` from DOI-url when serializing
- fix: show `<LomStats />` also when no `createdDate`
- fix: remove `defaultValue` when `value` exists
- fix: pass props that prop-types marks as required
- fix: mark `closeAction` as optional
- fix: create full record rather than just metadata
- `LOMRecordData`: add fields from `self` to `.json`
- CI: lint javascript with `eslint`
- search-ui: remove field that LOM doesn't have
- react: don't use array-index as key
- react: destructure props
- js: use erroneously unused variables
- js: use camelCase
- react: add defaultProps
- react: add propTypes
- fix: request our custom mime-type in `EditButton`
- fix: realign signature of file-preview view-function
- fix: use `dict` for `RequestParser` args
- fix: re-align function signature with marshmallow
- fix: typo in entrypoints
- update: negotiate custom mimetype
- fix: finalize api-app too
- fix: remove `()` from `@pytest.fixture()`
- permission: change inheritance



Version v0.16.0 (release 2024-07-05)

- upgrade: add script to upgrade parent
- metadata: add method get_courses
- fix: deduped assume parent is a list
- fix: metadata rights not exists use param
- fix: missed removing metadata attribute usage
- utils: add LOMRecordData class
- utils: add create_record and update_record func
- services: move add identifier to components
- setup: move to python3.12 only


Version v0.15.2 (release 2024-06-18)

- oai: add missing function for getrecords
- oai: fix doi not exists
- fix: import deposit components from rdm


Version v0.15.1 (release 2024-06-13)

- fix: typo on attribute name
- add CC0 to license selection


Version v0.15.0 (release 2024-05-29)

- fix: update permission for manage
- if the entity is not a list what it should be it will be handled
  correctly
- the LOMMetadata handles now only the metadata
- add a function to check about duplicate entries

Version v0.14.0 (release 2024-05-06)

- modification: add statistic for a record


Version v0.13.5 (release 2024-04-23)

- oai: add date to contribute
- fix: vcard-serialization


Version v0.13.4 (release 2024-03-08)

- deps: add missing dependency


Version v0.13.3 (release 2024-03-08)

- fix: oai-pmh no centity
- configure permissions newly added to invenio


Version v0.13.2 (release 2024-02-27)

- mark user-visible errors for translation
- replace deprecated importlib.resources.open_text
- sanitize data coming from upload-page


Version v0.13.1 (release 2024-02-13)

- fix: method returns valid value


Version v0.13.0 (release 2024-02-12)

- oai: rebuild schema to dump
- tests: update run-tests to invenio standard
- refactore: serializers to rdm-records structure
- black: fix formating v24.1.1


Version v0.12.3 (release 2024-01-11)

- fix: indexer needs queue name


Version v0.12.2 (release 2024-01-07)

- fix: rebuild-index not working
- setup: add support for python3.10 and 3.11
- wording: change


Version v0.12.1 (release 2023-12-01)

- standardize rights-URLs passed to `LOMMetadata`
- alembic: add deletion_status field
- modification: alembic scripts


Version v0.12.0 (release 2023-11-09)

- setup: temporary remove python3.10
- fix: errors (mostly pylint)
- setup: remove test upper bounds
- cli: add parameter to create demo in backend
- ui: add new button to user dashboard
- search: add configuration for dashboard search
- permissions: change can_read_draft
- ui: redesign EditButton
- fix: version is an object
- compatibility: add attributes for rdm-records
- ui: add collapsable facets
- resources: add dublin core schema
- global: change prefix, add user_dashboard
- ui: change route prefix
- dashboard: change text
- services: make components configurable
- compatibility: change import paths
- refactor: remove unused file
- global: move jsonschemas to records
- global: migrate to invenio_i18n (flask-babel)
- setup: remove rdm-records boundary
- metadata: add methods
- stop grouping lifecycle.contributes by role
- stop grouping for data from upload-page
- stop grouping for data built with LOMMetadata
- group on OAI-PMH output computation to retain compatibility
- clean up file headers
- clean up config files


Version v0.11.1 (release 2023-08-03)

- fix: licenses url with slash as last character


Version v0.11.0 (release 2023-08-03)

- fix: license facets trailing slash
- fix: translation was configured wrong
- ui: remove current_user.id, not used
- ui: show management only if allowed
- fix: deposit edit needs permissions
- ui: add edit-button of records


Version v0.10.1 (release 2023-07-25)

- fix: use save key access


Version v0.10.0 (release 2023-07-25)

- translation: update
- refactor:
- ui: add doi to sidemenu
- tests: add pylint disable statements
- setup: use pytest-black-ng instead of pytest-black
- ui: add classification and course to landing page
- metadata: reimplement dedup for append_course
- metadata: change metadata a little bit
- refactor: remove python3.8 compatibility
- implement and configure facets (=search-filters)
- clean up various upload-page related things
- implement vcard and use it for OAI-PMH-output


Version v0.9.0 (release 2023-06-01)

- add `format` and `resource-type` to upload-page
- add schema for cleaner OAI-PMH-output
- add "$schema"-key to jsons in database
- update landing page
- implement and configure permissions
- fix image-preview by implementing iiif-resource


Version v0.8.1 (release 2023-04-28)

- upload: require license permission


Version v0.8.0 (release 2023-04-20)

- make compatible with invenio v11
- support DOI, publishing, deleting


Version v0.7.2 (release 2023-03-15)

- fix file-upload


Version v0.7.1 (release 2023-03-13)

- add .js-files that were erroneously missing from last PR


Version v0.7.0 (release 2023-03-13)

- global: fix various problems
- finish preview of deposit for test-server


Version v0.6.1 (release 2023-02-01)

- fix: pylint errors
- fix: syntax error in setup.cfg


Version v0.6.0 (release 2022-10-14)

- global: migrate to reusable workflows for publish
- typo: fixed wrong position of .
- test: move to reusable workflows
- tests: remove CACHE
- fix: change opensearch2 to opensearch in run-tests
- global: replace elasticsearch7 with opensearch2
- setup: update dependencies


Version v0.5.2 (release 2022-09-27)

- fix: javascript dependencies


Version v0.5.1 (release 2022-09-27)

- fix: pylint errors
- fix: ConfigurationMixin changed location
- global: pin flake8
- global: increase version of invenio-search


Version v0.5.0 (release 2022-07-29)

- fix missing schema for type link
- add the search feature
- update UI-serialization and landing page


Version v0.3.1 (release 2022-06-01)

- update publish action
- fix combined fixes

