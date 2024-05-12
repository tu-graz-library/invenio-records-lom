# -*- coding: utf-8 -*-
#
# Copyright (C) 2021-2024 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""LOM resources."""

from flask_resources import route
from invenio_rdm_records.resources import RDMRecordResource


class LOMRecordResource(RDMRecordResource):
    """LOM Record resource."""

    def create_url_rules(self) -> list:
        """Create the URL rules for the record resource."""

        def s(route: str) -> str:
            """Suffix a route with the URL prefix."""
            return f"{route}{self.config.url_prefix}"

        def prefix(route: str) -> str:
            """Prefix a route with `self.config.prefix`."""
            return f"{self.config.url_prefix}{route}"

        routes = self.config.routes
        return [
            route("DELETE", prefix(routes["item-pids-reserve"]), self.pids_discard),
            route("DELETE", prefix(routes["item-draft"]), self.delete_draft),
            route("GET", prefix(routes["list"]), self.search),
            route("GET", prefix(routes["item"]), self.read),
            route("POST", prefix(routes["list"]), self.create),
            route("POST", prefix(routes["item-draft"]), self.edit),
            route("POST", prefix(routes["item-publish"]), self.publish),
            route("POST", prefix(routes["item-pids-reserve"]), self.pids_reserve),
            route("PUT", prefix(routes["item-draft"]), self.update_draft),
            # User Dashboard routes
            route("GET", s(routes["user-prefix"]), self.search_user_records),
        ]
