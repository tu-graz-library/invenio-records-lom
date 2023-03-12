# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
#
# Copyright (C) 2021-2023 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for
# more details.

"""JS/CSS Webpack bundles for theme."""

from invenio_assets.webpack import WebpackThemeBundle

theme = WebpackThemeBundle(
    __name__,
    "assets",
    default="semantic-ui",
    themes={
        # theme-name ~> kwargs_for_WebpackBundle
        "semantic-ui": {
            "aliases": {},
            "entry": {
                "invenio-records-lom-deposit": "./js/invenio_records_lom/deposit/index.js",
                "invenio-records-lom-search": "./js/invenio_records_lom/search/index.js",
                "invenio-records-lom-theme": "./less/invenio_records_lom/theme.less",
            },
            "dependencies": {
                "@babel/runtime": "^7.9.0",
                "react": "^16.13.0",
                "react-dom": "^16.13.0",
            },
            "devDependencies": {},
            "peerDependencies": {},
        },
    },
)
