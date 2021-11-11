# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

""""""

from flask_resources import route
from invenio_drafts_resources.resources import RecordResource


class LOMRecordResource(RecordResource):
    def create_url_rules(self):
        def p(route):
            """Prefix a route with `self.config.prefix`."""
            return f"{self.config.url_prefix}{route}"

        routes = self.config.routes
        return [
            route("GET", p(routes["item"]), self.read),
        ]
