# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.


"""invenio data model for Learning object metadata."""

from .ext import InvenioRecordsLOM
from .proxies import current_records_lom

__version__ = "0.18.1"

__all__ = (
    "InvenioRecordsLOM",
    "__version__",
    "current_records_lom",
)
