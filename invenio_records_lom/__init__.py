# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.


"""invenio data model for Learning object metadata."""

from .ext import InvenioRecordsLOM
from .proxies import current_records_lom

__version__ = "0.17.0"

__all__ = (
    "__version__",
    "current_records_lom",
    "InvenioRecordsLOM",
)
