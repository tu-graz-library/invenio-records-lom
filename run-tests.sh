#!/usr/bin/env bash
# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

pydocstyle invenio_records_lom tests docs && \
isort -rc -c -df && \
check-manifest --ignore ".travis-*,docs/_build*" && \
sphinx-build -qnNW docs docs/_build/html && \
python setup.py test
