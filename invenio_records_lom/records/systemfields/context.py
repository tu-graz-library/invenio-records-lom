# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Context for LOM PID-fields.

With this context given, the resolver uses the "lomid" PID type.
"""

from invenio_records_resources.records.systemfields.pid import PIDFieldContext


class LOMPIDFieldContext(PIDFieldContext):
    """PIDField context_cls for LOM drafts/records.

    With this context given, the resolver uses the "lomid" PID type.
    """

    pid_type = "lomid"
