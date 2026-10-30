# SPDX-FileCopyrightText: 2022 Northwestern University.
# SPDX-FileCopyrightText: 2020-2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""DataCite DOI Client."""

from unittest.mock import Mock

from idutils import normalize_doi
from invenio_rdm_records.services.pids import providers


class FakeDataCiteRESTClient:
    """DataCite REST API client wrapper."""

    def __init__(self, prefix: str, *_: dict, **__: dict) -> None:
        """Initialize the REST client wrapper."""
        self.prefix = prefix

    def public_doi(self, *_: dict, **__: dict) -> Mock:
        """Create a public doi ... not."""
        return Mock()

    def update_doi(self, *_: dict, **__: dict) -> Mock:
        """Update the metadata or url for a DOI ... not."""
        return Mock()

    def delete_doi(self, *_: dict, **__: dict) -> Mock:
        """Delete a doi ... not."""
        return Mock()

    def hide_doi(self, *_: dict, **__: dict) -> Mock:
        """Hide a previously registered DOI ... not."""
        return Mock()

    def show_doi(self, *_: dict, **__: dict) -> Mock:
        """Show a previously hidden DOI ... not."""
        return Mock()

    def check_doi(self, doi: str) -> str:
        """Check doi structure.

        Check that the doi has a form
        12.12345/123 with the prefix defined
        """
        # If prefix is in doi
        if "/" in doi:
            split = doi.split("/")
            prefix = split[0]
            if prefix != self.prefix:
                # Provided a DOI with the wrong prefix
                msg = f"Wrong DOI {prefix} prefix provided, it should"
                " be {self.prefix} as defined in the rest client"
                raise ValueError(msg)
        else:
            doi = f"{self.prefix}/{doi}"
        return normalize_doi(doi)


class FakeDataCiteClient(providers.DataCiteClient):
    """Fake DataCite Client."""

    @property
    def api(self) -> FakeDataCiteRESTClient:
        """DataCite REST API client instance."""
        self.check_credentials()
        return FakeDataCiteRESTClient(self.cfg("prefix"))
