# SPDX-FileCopyrightText: 2024-2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Datacite serializer."""

from flask_resources import JSONSerializer, MarshmallowSerializer

from .schema import LOMToDataCite44Schema


class LOMToDataCite44Serializer(MarshmallowSerializer):
    """Marshmallow-based DataCite-serializer for LOM records."""

    def __init__(self, **kwargs: dict) -> None:
        """Construct."""
        super().__init__(
            format_serializer_cls=JSONSerializer,
            object_schema_cls=LOMToDataCite44Schema,
            **kwargs,
        )

    # TODO: Remove when
    # invenio_rdm_records.services.pids.providers.datacite.DataCitePIDProvider
    # uses the new MarshmallowSerializer class
    def dump_one(self, obj: dict) -> dict:
        """Dump the object with extra information."""
        return self.dump_obj(obj)
