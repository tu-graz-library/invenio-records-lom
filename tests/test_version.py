# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 Nikita Lvov.
#
# tug_lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Simple test of version import."""

from __future__ import absolute_import, print_function


def test_version():
    """Test version import."""
    from tug_lom import __version__
    assert __version__
