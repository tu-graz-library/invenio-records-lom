# SPDX-FileCopyrightText: 2021-2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

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
            route("DELETE", prefix(routes["item-draft"]), self.delete_draft),
            route("GET", prefix(routes["list"]), self.search),
            route("GET", prefix(routes["item"]), self.read),
            route("POST", prefix(routes["list"]), self.create),
            route("POST", prefix(routes["item-draft"]), self.edit),
            route("GET", prefix(routes["item-draft"]), self.read_draft),
            route("POST", prefix(routes["item-publish"]), self.publish),
            route("PUT", prefix(routes["item-draft"]), self.update_draft),
            # User Dashboard routes
            route("GET", s(routes["user-prefix"]), self.search_user_records),
            route("POST", prefix(routes["item-pids-reserve"]), self.pids_reserve),
        ]

    # TODO: some parent-methods have @response_header_signposting,
    #   which adds an 'Link'-HTTP-header that is incorrect for LOM...
