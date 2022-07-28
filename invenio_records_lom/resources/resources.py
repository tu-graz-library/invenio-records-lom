# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""LOM resources."""

from flask_resources import route
from invenio_drafts_resources.resources import RecordResource


class LOMRecordResource(RecordResource):
    """LOM Record resource."""

    def create_url_rules(self):
        """Create the URL rules for the record resource."""

        def prefix(route_str):
            """Prefix a route with `self.config.prefix`."""
            return f"{self.config.url_prefix}{route_str}"

        routes = self.config.routes
        return [
            route("GET", prefix(routes["list"]), self.search),
            route("GET", prefix(routes["item"]), self.read),
        ]
