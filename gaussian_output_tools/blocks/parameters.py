from __future__ import annotations  # will be default in Python 3.10

from dataclasses import dataclass
from decimal import Decimal
from typing import Iterator, List, Optional, Tuple, Union, cast
import sys

import regex as re

from . import UREG, Match

PARAMETERS_MATCH = re.compile(
    r"""
^\s*-+ \s*
!\s+ (?P<type>Optimized|Initial)\ Parameters \s+!\n
(?:.+\n){3}
\s-+\n
( \s!\s
  (?P<name>\S+) \s+
  (?P<definition>\S+) \s+
  (?P<value>\S+) \s+
  (?P<derivativeinfo>.+?)\s+
  ! \n )+
\s-+\n""",
    re.VERBOSE | re.MULTILINE,
)


@dataclass
class ParameterEntry:
    name: str
    definition: str
    value: Decimal
    derivative_info: Union[Tuple[str, Decimal], str]

    @classmethod
    def from_match(
        cls,
        name: str,
        definition: str,
        value: str,
        derivinfo: Union[str, Tuple[str, Decimal]],
    ) -> ParameterEntry:
        try:
            deriv, val = cast(str, derivinfo).split("=")
            derivinfo = (deriv.strip(), Decimal(val))
        except ValueError:
            pass

        if definition.startswith(("R", "B")):
            unit = UREG.angstrom
        elif definition.startswith(("A", "D", "L")):
            unit = UREG.degree
        else:
            raise AssertionError(
                f"unknown structural parameter definition: {definition}"
            )

        return cls(name, definition, Decimal(value) * unit, derivinfo)


@dataclass
class Parameters:
    type: str
    entries: List[ParameterEntry]


def match_parameters(
        content: str, start: int = 0, end: int = sys.maxsize
) -> Iterator[Match]:
    for match in PARAMETERS_MATCH.finditer(content, start, end):
        yield Match(
            data=Parameters(
                type=match["type"],
                entries=[
                    ParameterEntry.from_match(name, defin, val, di)
                    for name, defin, val, di in zip(
                        *match.captures("name", "definition", "value", "derivativeinfo")
                    )
                ],
            ),
            spans=match.spans(),
        )
