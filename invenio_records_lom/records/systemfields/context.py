# SPDX-FileCopyrightText: 2021-2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""Context for LOM PID-fields.

With this context given, the resolver uses the "lomid" PID type.
"""

from invenio_records_resources.records.systemfields.pid import PIDFieldContext


class LOMPIDFieldContext(PIDFieldContext):
    """PIDField context_cls for LOM drafts/records.

    With this context given, the resolver uses the "lomid" PID type.
    """

    pid_type = "lomid"
