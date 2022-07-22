# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.


"""invenio data model for Learning object metadata."""

from flask import render_template


def search():
    """Search help guide."""
    return render_template("invenio_records_lom/search.html")
