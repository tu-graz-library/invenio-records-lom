# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Customized classes used by pids-service."""

from flask_babelex import lazy_gettext as _
from invenio_rdm_records.services.pids.providers import DataCitePIDProvider


class LOMDataCitePIDProvider(DataCitePIDProvider):
    """DataCite pid provider with customized validate.

    LOM-datamodel stores the publisher at another location,
    hence another validation is needed.
    """

    def validate(self, record, identifier=None, provider=None, **kwargs):
        """Validate the attributes of the identifier.

        :returns: A tuple (success, errors). `success` is a bool that specifies
                  if the validation was successful. `errors` is a list of
                  error dicts of the form:
                  `{"field": <field>, "messages: ["<msgA1>", ...]}`.
        """
        # skip direct parent-class's validate, but do parent's parent
        success, errors = super(DataCitePIDProvider, self).validate(
            record, identifier, provider, **kwargs
        )

        # check format, as in parent.validate
        if identifier is not None:
            try:
                self.client.api.check_doi(identifier)
            except ValueError as e:
                # modifies the error in errors in-place
                self._insert_pid_type_error_msg(errors, str(e))

        # validate record
        serializer = self.serializer
        schema = serializer.object_schema_cls(context=serializer.schema_context)
        try:
            publisher = schema.fields["publisher"].serialize(None, record)
            if not publisher:
                raise ValueError("No publisher serializable from passed-in `record`.")
        except Exception:  # pylint: disable='broad-exception-caught
            errors.append(
                {
                    "field": "metadata.publisher",  # use invenio's field-name for compatibility
                    "messages": [_("Missing publisher.")],
                }
            )

        return success and not errors, errors
