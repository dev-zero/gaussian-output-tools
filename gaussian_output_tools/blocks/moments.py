from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, Iterator, Optional

import regex as re

from . import Match

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
        yield Match(
            data=Moment(
                type=match["type"],
                unit=match["unit"],
                notes=match["notes"],
                vals={k: Decimal(v) for k, v in zip(*match.captures("key", "val"))},
            ),
            spans=match.spans(),
        )
