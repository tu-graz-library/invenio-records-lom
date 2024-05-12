# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.


"""Utils tests."""


from invenio_records_lom.utils import DotAccessWrapper, LOMMetadata


def test_wrapper() -> None:
    """Test wrapper."""
    data = {
        "a": {
            "b": ["c", "d"],
            "e": "f",
        },
    }
    wrapper = DotAccessWrapper(data)

    # getting
    assert wrapper["a.e"] == "f"
    assert wrapper["a.b.0"] == "c"

    # setting
    wrapper["a.e"] = "g"
    assert data["a"]["e"] == "g"
    wrapper["a.b.[]"] = "h"
    assert data["a"]["b"] == ["c", "d", "h"]
    wrapper["i.j"] = "k"
    assert data["i"]["j"] == "k"

    # deleting
    del wrapper["a.b.1"]
    assert "d" not in data["a"]["b"]

    # other dict-like functionality
    assert "a.e" in wrapper  # containment check


def test_oefosdict_getter() -> None:
    """Test loading OEFOS-dict."""
    oefos_dict_de = LOMMetadata.oefosdict_by_language["de"]
    oefos_dict_en = LOMMetadata.oefosdict_by_language["en"]

    assert oefos_dict_de["101001"] == "Algebra"
    assert oefos_dict_de["2"] == "TECHNISCHE WISSENSCHAFTEN"

    assert oefos_dict_en["2"] == "TECHNICAL SCIENCES"
