from dataclasses import dataclass
from decimal import Decimal
from typing import Iterator, List, Optional

import regex as re

from . import Match

DIPOLE_MATCH = re.compile(
    r"""
(
  \ Dipole\ orientation:\n
  (?:\s* (?P<oanr>\d+) (?:\s+ (?P<oval>\S+)){3} \n)+
  \n
)?
\ Electric\ dipole\ moment\ \((?P<orientation>\w+)\ orientation\):\n
(?:.+\n){2}
(?:\s* (?P<direction>\w+) (?:\s+ (?P<val>\S+)){3} \n)+
\n
\ Dipole\ polarizability,\ (?P<spin>\w+)\ .+\n
(?:.+\n){3}
(?:\s* (?P<pdirection>\w+) (?:\s+ (?P<pval>\S+)){3} \n)+
""",
    re.VERBOSE | re.MULTILINE,
)


@dataclass
class AtomCoords:
    nr: int
    x: Decimal
    y: Decimal
    z: Decimal


@dataclass
class Moment:
    """Electric dipole moment in a.u."""

    tot: Decimal
    x: Decimal
    y: Decimal
    z: Decimal


@dataclass
class Polarizability:
    """Dipole polarizability in a.u."""

    spin: str
    iso: Decimal
    aniso: Decimal
    xx: Decimal
    yx: Decimal
    yy: Decimal
    xz: Decimal
    zy: Decimal
    zz: Decimal


@dataclass
class Dipole:
    orientation: str
    atom_orientation: Optional[List[AtomCoords]]
    moment: Moment
    polarizability: Polarizability


def match_dipole(
    content: str, start: Optional[int] = None, end: Optional[int] = None
) -> Iterator[Dipole]:
    for match in DIPOLE_MATCH.finditer(content, start, end):

        if match.captures("oval"):
            coord_len = len(match.captures("oval"))
            atom_orientation = [
                AtomCoords(int(oanr), *(Decimal(v) for v in oval))
                for oanr, oval in zip(
                    match.captures("oanr"),
                    (
                        match.captures("oval")[idx : idx + 3]
                        for idx in range(0, coord_len, 3)
                    ),
                )
            ]
        else:
            atom_orientation = None

        moment = Moment(
            *(Decimal(v.replace("D", "E")) for v in match.captures("val")[::3])
        )
        polarizability = Polarizability(
            match["spin"],
            *(Decimal(val.replace("D", "E")) for val in match.captures("pval")[::3]),
        )

        yield Match(
            data=Dipole(match["orientation"], atom_orientation, moment, polarizability),
            spans=match.spans(),
        )
