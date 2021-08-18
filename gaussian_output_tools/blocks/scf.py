from dataclasses import dataclass
from decimal import Decimal
from typing import Iterator, Optional

import regex as re

from . import UREG, Match

SCF_MATCH = re.compile(
    r"""
^\ SCF\ Done: \ + E\((?P<type>\S+)\)\ = \s* (?P<energy>\S+) \s+(?P<unit>\S+) .+\n
\ +NFock=\ *\d+\ +Conv=(?P<conv>\S+) .+ \n
(?P<conv_failure>\ Convergence\ failure.+)?
""",
    re.VERBOSE | re.MULTILINE,
)


@dataclass
class SCF:
    type: str
    energy: Decimal
    convergence: Decimal
    succeeded: bool


def match_scf(
    content: str, start: Optional[int] = None, end: Optional[int] = None
) -> Iterator[Match]:

    for match in SCF_MATCH.finditer(content, start, end):
        res = SCF(
            type=match["type"],
            energy=Decimal(match["energy"].replace("D", "E")) * UREG.hartree,
            convergence=Decimal(match["conv"].replace("D", "E")),
            succeeded=True if match["conv_failure"] is None else False,
        )

        yield Match(data=res, spans=match.spans())
