# -*- coding: utf-8 -*-
#
# Copyright (C) 2023-2024 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""VCard tests."""
from invenio_records_lom.utils.vcard import VCardMaker, VCardProperty, make_lom_vcard


def test_basic_vcard() -> None:
    """Test most basic `VCard`-creation."""
    vcard: str = make_lom_vcard(fn="Value of *Formatted Name* property")
    assert vcard == (
        "BEGIN:VCARD\n"
        "VERSION:4.0\n"
        "FN:Value of *Formatted Name* property\n"
        "END:VCARD"
    )


def test_escaping() -> None:
    """Test whether special symbols are indeed escaped."""
    vcard: str = make_lom_vcard(
        fn="Commas (,), backslashes (\\), and new-lines (\n) must be escaped",
    )
    assert vcard == (
        "BEGIN:VCARD\n"
        "VERSION:4.0\n"
        "FN:Commas (\\,)\\, backslashes (\\\\)\\, and new-lines (\\n) must be escaped\n"
        "END:VCARD"
    )


def test_line_wrapping() -> None:
    """Test whether long lines wrap correctly."""
    vcard: str = make_lom_vcard(
        fn="Name so long that the `FN:<this name>` line has more than 75 octets"
        " in its utf-8 encoding, which will cause line-wrapping",
    )
    # cuts off in the middle of the word
    # wrapped line starts with an extra space
    assert vcard == (
        "BEGIN:VCARD\n"
        "VERSION:4.0\n"
        "FN:Name so long that the `FN:<this name>` line has more than 75 octets in i\n"
        " ts utf-8 encoding\\, which will cause line-wrapping\n"
        "END:VCARD"
    )


def test_advanced_vcard() -> None:
    """Test whether singular features also work together in concert."""
    vcard: str = make_lom_vcard(
        fn="Long name as to cause line-wrapping, also includes special symbols for escaping (like \\, \n).",
        n=[
            [
                "surname,comma",
                "first;semicolon",
                "title\nnewline",
                "honorific\\backslash",
                "lengthening for wrap",
            ],  # note: nested list to test compounding
        ],
        email=["first@mail.org", "second@mail.org"],
    )
    assert vcard == (
        "BEGIN:VCARD\n"
        "VERSION:4.0\n"
        "FN:Long name as to cause line-wrapping\\, also includes special symbols for \n"
        " escaping (like \\\\\\, \\n).\n"
        "N:surname\\,comma;first\\;semicolon;title\\nnewline;honorific\\\\backslash;lengt\n"
        " hening for wrap\n"
        "EMAIL:first@mail.org\n"
        "EMAIL:second@mail.org\n"
        "END:VCARD"
    )


def test_custom_vcard() -> None:
    """Test customized VCard-creation."""
    custom_config = {
        "fn": VCardProperty(compoundable=False, min=1),
        "custom": VCardProperty(compoundable=True),
    }
    maker = VCardMaker(
        final_line_break=True,
        line_break_str="\r\n",
        output_encoding="utf-8",
        properties_config=custom_config,
    )
    vcard: bytes = maker.make_vcard(fn="fn", custom=[["a", "b"], ["c", "d"]])
    assert vcard == (
        b"BEGIN:VCARD\r\n"
        b"VERSION:4.0\r\n"
        b"FN:fn\r\n"
        b"CUSTOM:a;b\r\n"
        b"CUSTOM:c;d\r\n"
        b"END:VCARD\r\n"
    )
