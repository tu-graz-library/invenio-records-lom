# SPDX-FileCopyrightText: 2020-2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""invenio data model for Learning object metadata."""

from .ext import InvenioRecordsLOM
from .proxies import current_records_lom

__version__ = "0.23.2"

__all__ = (
    "InvenioRecordsLOM",
    "__version__",
    "current_records_lom",
)
