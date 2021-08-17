from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, Iterator, Optional

import regex as re

from . import UREG, Match

MOMENT_MATCH = re.compile(
    r"""
^\s*(?P<type>[\w ]+)\ moment\ \((?P<notes>[^)]+),\ (?P<unit>[^)]+)\):\s*
(?:
  \s+ (?P<key>[XYZ]+|Tot)= \s+ (?P<val>[+-]?([0-9]+([.][0-9]*)?|[.][0-9]+))
)+
""",
    re.VERBOSE | re.MULTILINE,
)


@dataclass
class Moment:
    type: str
    unit: str
    notes: str
    vals: Dict[str, Decimal]


def match_moments(
    content: str, start: Optional[int] = None, end: Optional[int] = None
) -> Iterator[Match]:
    for match in MOMENT_MATCH.finditer(content, start, end):
        moment_type = match["type"]
        if moment_type == "Dipole":
            unit = UREG.debye
        elif "Quadrupole" in moment_type:
            unit = UREG.debye * UREG.angstrom
        elif moment_type == "Octapole":
            unit = UREG.debye * UREG.angstrom ** 2
        elif moment_type == "Hexadecapole":
            unit = UREG.debye * UREG.angstrom ** 3
        else:
            raise AssertionError(f"unsupported momen type: {moment_type}")

        yield Match(
            data=Moment(
                type=moment_type,
                unit=match["unit"],
                notes=match["notes"],
                vals={
                    k: Decimal(v) * unit for k, v in zip(*match.captures("key", "val"))
                },
            ),
            spans=match.spans(),
        )
