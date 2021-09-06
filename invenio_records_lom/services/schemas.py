# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Marshmallow schema for validating LOM JSONs."""

from marshmallow import Schema


class LOMRecordSchema(Schema):
    """Marshmallow schema for validating LOM JSONs."""

    # TODO: write schema

    def load(self, data, *, many=None, partial=None, unknown=None):
        """Overwrite validation: pipe data through unchanged and unvalidated for now."""
        return data

    # TODO: is: (obj: LOMDraft) -> LOMDraft; should be: (obj: LOMDraft) -> json
    def dump(self, obj, *, many=None):
        """Overwrite validation: pipe obj through unchanged and unvalidated for now."""
        return obj
