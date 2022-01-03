from __future__ import annotations  # will be default in Python 3.10

import sys
from dataclasses import dataclass
from decimal import Decimal
from typing import Iterator, List

import regex as re

from . import UREG, Match

ORIENTATION_MATCH = re.compile(
    r"""
^\s+ (?P<type>Input|Standard)\ orientation: \s*\n
\s-+\n
(.+\n){2}
\s-+\n
(
  \s+ (?P<center_number>\S+)
  \s+ (?P<atomic_number>\S+)
  \s+ (?P<atomic_type>\S+)
  \s+ (?P<x>\S+)
  \s+ (?P<y>\S+)
  \s+ (?P<z>\S+)
  \n
)+
\s-+\n
""",
    re.VERBOSE | re.MULTILINE,
)


@dataclass
class OrientationEntry:
    center_number: int
    atomic_number: int
    atomic_type: int
    x: Decimal
    y: Decimal
    z: Decimal

    @classmethod
    def from_match(
        cls,
        center_number: str,
        atomic_number: str,
        atomic_type: str,
        x: str,
        y: str,
        z: str,
    ) -> OrientationEntry:
        return cls(
            int(center_number),
            int(atomic_number),
            int(atomic_type),
            Decimal(x) * UREG.angstrom,
            Decimal(y) * UREG.angstrom,
            Decimal(z) * UREG.angstrom,
        )


@dataclass
class Orientation:
    type: str
    entries: List[OrientationEntry]


def match_orientation(
    content: str, start: int = 0, end: int = sys.maxsize
) -> Iterator[Match]:
    for match in ORIENTATION_MATCH.finditer(content, start, end):
        yield Match(
            data=Orientation(
                type=match["type"],
                entries=[
                    OrientationEntry.from_match(cn, an, at, x, y, z)
                    for cn, an, at, x, y, z in zip(
                        *match.captures(
                            "center_number",
                            "atomic_number",
                            "atomic_type",
                            "x",
                            "y",
                            "z",
                        )
                    )
                ],
            ),
            spans=match.spans(),
        )
