# -*- coding: utf-8 -*-
#
# Copyright (C) 2023-2024 Graz University of Technology.
#
# invenio-records-lom is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Module with utilities for handling `vCard` version 4.0.

(see `RFC6350 <https://www.rfc-editor.org/rfc/rfc6350>`_ for the spec).

Usually, :py:func:`make_lom_vcard` should be what you need.

.. code-block:: python

   # can be used directly, without any setup:
   vcard = make_lom_vcard(
       fn='Firstname Lastname",
       email="person@company.com",
       **other_configured_properties,
   )
   # `vcard`'s type will be `str`

To configure how VCards are made, create your own :py:class:`VCardMaker`,
then use its :py:meth:`~VCardMaker.make_vcard` method:

.. code-block:: python

   my_vcard_maker = VCardMaker(**my_config)
   vcard = my_vcard_maker.make_vcard(**configured_vcard_properties)
   # `vcard`'s type will be type `str` or `bytes`, depending on `my_config`
   # which vcard-properties can be passed depends on `my_config`
"""

from collections.abc import Iterable
from dataclasses import dataclass


@dataclass(frozen=True)
class VCardProperty:
    """Holds configuration for a vcard property."""

    compoundable: bool = False
    min: int = 0
    # just some sufficiently high number for properties that can
    # appear arbitrarily often
    max: int = 255


DEFAULT_PROPERTIES_CONFIG: dict[str, VCardProperty] = {
    "fn": VCardProperty(compoundable=False, min=1),  # stands for `formatted name`
    "n": VCardProperty(compoundable=True, max=1),  # stands for `name`
    "email": VCardProperty(),
    "role": VCardProperty(),
}


class VCardMaker:
    """Utility for making vcards version 4.0.

    (see `RFC 6350 <https://www.rfc-editor.org/rfc/rfc6350>`_ for the spec).

    Defaults for arguments follow the spec.

    :param bool final_line_break: whether to include a line-break after the final line
    :param str line_break_str: which string to use for line-breaks

    :param None | str output_encoding: output will be a
                      ``bytes``-object encoded with this encoding, set to ``None`` to
                      output a ``str``-object instead

    :param None | dict[str, VCardProperty] properties_config: configures which
                                           vcard-properties are allowed and how to
                                           build them
    """

    def __init__(
        self,
        *,
        final_line_break: bool = True,
        line_break_str: str = "\r\n",
        output_encoding: None | str = "utf-8",
        properties_config: None | dict[str, VCardProperty] = None,
    ) -> None:
        """Init."""
        self.final_line_break = final_line_break
        self.line_break_str = line_break_str
        self.output_encoding = output_encoding
        if properties_config is None:
            self.properties_config = DEFAULT_PROPERTIES_CONFIG
        else:
            self.properties_config = properties_config

    def __repr__(self) -> str:
        """Repr."""
        return (
            f"{self.__class__.__name__}("
            f"final_line_break={self.final_line_break!r}, "
            f"line_break_str={self.line_break_str!r}, "
            f"output_encoding={self.output_encoding!r}, "
            f"properties_config={self.properties_config!r})"
        )

    @staticmethod
    def escape(vcard_property: str, *, is_component: bool) -> None:
        r"""Escape a vcard property.

        ``\``, ``\n``, and ``,`` are always escaped.
        ``;`` is additionally escaped iff ``is_component`` is truthy.
        """
        vcard_property = (
            vcard_property.replace("\\", "\\\\")
            .replace(",", "\\,")
            .replace("\n", "\\n")
        )

        if is_component:
            vcard_property = vcard_property.replace(";", "\\;")

        return vcard_property

    @staticmethod
    def utf_8_len(s: str) -> int:
        """Return length of `s` in number of octets `s`'s "utf-8"-encoding has."""
        return len(s.encode(encoding="utf-8"))

    def line_wrap(self, unwrapped_vcard: str) -> str:
        """Wrap lines as per vcard-spec.

        - line-length in "utf-8"-encoding may not be longer than 75 octets
          (excluding newline-characters)
        - can't break apart multi-octet-sequences when line-wrapping
        - continued lines start with a space-character
        """
        input_lines = [line.lstrip() for line in unwrapped_vcard.splitlines()]
        output_lines = []
        for input_line in input_lines:
            start = 0  # index where currently built line starts

            # prefix of currently built line, space for continued lines,
            # counts towards line-length
            prefix = ""

            # length of currently built line, in number of "utf-8"-octets
            # in its "utf-8" encoding
            length = 0

            idx = 0  # index running through `input_line`
            while idx < len(input_line):
                char = input_line[idx]
                length += self.utf_8_len(char)
                if length > 75:  # noqa: PLR2004
                    # `char` would push currently built line over limit
                    output_lines.append(prefix + input_line[start:idx])
                    start = idx
                    prefix = " "
                    length = self.utf_8_len(prefix)
                else:
                    idx += 1
            # handle rest of `input_line`
            output_lines.append(prefix + input_line[start:])

        return self.line_break_str.join(output_lines) + (
            self.line_break_str if self.final_line_break else ""
        )

    def make_vcard(
        self,
        **vcard_properties: str | Iterable[str | Iterable[str]],
    ) -> str | bytes:
        r"""Build a vcard-string out of passed-in vcard properties.

        Some properties may occur in vcards multiple times.
        Call with a ``list[str]`` to get multiple occurances.
        Some properties (called *compound properties*) may consist of components.
        Call with a ``list[list[str]]`` to have the inner list interpreted as
        components.

        .. code-block:: python

                # make_vcard(**kwargs)  # line(s) created due to `kwargs`
                make_vcard(prop='a')  # 'PROP:a\n'
                make_vard(prop=['a', 'b'])  # 'PROP:a\nPROP:b\n'
                make_vcard(prop=[['a','b'], 'c'])  # 'PROP:a;b\nPROP:c\n'

        :return: built vcard, if `self.output_encoding` is truthy, encode output before
        return
        """
        # check: required properties exist
        required_properties = {
            name for name, config in self.properties_config.items() if config.min > 0
        }
        if missing_properties := sorted(required_properties - set(vcard_properties)):
            msg = f"missing required properties: {missing_properties!r}"
            raise TypeError(msg)

        # check: passed properties have configuration
        for name in vcard_properties:
            if name not in self.properties_config:
                msg = f"got keyword argument without corresponding configuration: {name!r}"
                raise TypeError(msg)

        # convert to lines
        lines: list[str] = ["BEGIN:VCARD", "VERSION:4.0"]
        for name, value in vcard_properties.items():
            config = self.properties_config[name]

            # pack str-input, convert Iterable to list
            occurances: list[str | Iterable[str]] = (
                [value] if isinstance(value, str) else list(value)
            )
            if not config.min <= len(occurances) <= config.max:
                msg = f"property {name!r} can't occur {len(occurances)} times"
                raise ValueError(msg)

            for occurance in occurances:
                if not isinstance(occurance, str):
                    # `occurance` is an iterable of components
                    occurance_temp_list = list(occurance)
                    if len(occurance_temp_list) > 1 and not config.compoundable:
                        msg = f"got multiple components for non-compound property {name!r}"
                        raise TypeError(msg)
                    occurance_str = ";".join(
                        self.escape(comp, is_component=config.compoundable)
                        for comp in occurance_temp_list
                    )
                else:
                    # `occurance` is a str
                    occurance_str = self.escape(
                        occurance,
                        is_component=config.compoundable,
                    )
                lines.append(f"{name.upper()}:{occurance_str}")
        lines.append("END:VCARD")

        # join lines
        unwrapped_vcard = self.line_break_str.join(lines)

        # wrap lines
        vcard = self.line_wrap(unwrapped_vcard)

        if self.output_encoding:
            return vcard.encode(encoding=self.output_encoding)
        return vcard


def make_lom_vcard(**vcard_properties: str | Iterable[str]) -> str | bytes:
    """Build a vcard out of passed-in properties.

    Internally uses a :py:class:`VCardMaker` configured for use with this package.
    """
    lom_vcard_maker = VCardMaker(
        final_line_break=False,
        line_break_str="\n",
        output_encoding=None,
        properties_config=None,
    )

    return lom_vcard_maker.make_vcard(**vcard_properties)
