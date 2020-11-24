# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.


"""invenio data model for Learning object metadata."""

from __future__ import absolute_import, print_function

from .ext import LomRecords
from .proxies import Lom, current_lomrecord
from .version import __version__

__all__ = ("__version__", "LomRecords", "Lom", "current_lomrecord")
