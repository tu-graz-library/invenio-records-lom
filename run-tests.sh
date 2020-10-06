#!/usr/bin/env bash
# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 Nikita Lvov.
#
# tug_lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

pydocstyle tug_lom tests docs && \
isort -rc -c -df && \
check-manifest --ignore ".travis-*,docs/_build*" && \
sphinx-build -qnNW docs docs/_build/html && \
python setup.py test
