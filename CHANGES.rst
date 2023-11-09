..
    Copyright (C) 2020 Graz University of Technology.

    invenio-records-lom is free software; you can redistribute it and/or modify it
    under the terms of the MIT License; see LICENSE file for more details.

Changes
=======

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

