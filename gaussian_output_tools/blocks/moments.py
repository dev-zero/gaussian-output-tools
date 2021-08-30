from dataclasses import dataclass
from decimal import Decimal
from typing import Iterator, Optional
import sys

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
class DipoleMoment:
    tot: Decimal
    x: Decimal
    y: Decimal
    z: Decimal


@dataclass
class QuadrupoleMoment:
    xx: Decimal
    yy: Decimal
    zz: Decimal
    xy: Decimal
    xz: Decimal
    yz: Decimal


@dataclass
class OctapoleMoment:
    xxx: Decimal
    yyy: Decimal
    zzz: Decimal
    xyy: Decimal
    xxy: Decimal
    xxz: Decimal
    xzz: Decimal
    yzz: Decimal
    yyz: Decimal
    xyz: Decimal


@dataclass
class HexadecapoleMoment:
    xxxx: Decimal
    yyyy: Decimal
    zzzz: Decimal
    xxxy: Decimal
    xxxz: Decimal
    yyyx: Decimal
    yyyz: Decimal
    zzzx: Decimal
    zzzy: Decimal
    xxyy: Decimal
    xxzz: Decimal
    yyzz: Decimal
    xxyz: Decimal
    yyxz: Decimal
    zzxy: Decimal


@dataclass
class Moments:
    dipole: DipoleMoment
    quadrupole: QuadrupoleMoment
    octopole: OctapoleMoment
    hexadecapole: HexadecapoleMoment


def match_moments(
        content: str, start: int = 0, end: int = sys.maxsize
) -> Iterator[Match]:
    spans = []

    def _unpack(match, unit):
        return {
            k.lower(): Decimal(v) * unit for k, v in zip(*match.captures("key", "val"))
        }

    moment_type = ""

    for match in MOMENT_MATCH.finditer(content, start, end):
        moment_type = match["type"]
        if moment_type == "Dipole":
            dipole = DipoleMoment(**_unpack(match, UREG.debye))
        elif "Quadrupole" in moment_type:
            quadrupole = QuadrupoleMoment(**_unpack(match, UREG.debye * UREG.angstrom))
        elif moment_type == "Octapole":
            octapole = OctapoleMoment(**_unpack(match, UREG.debye * UREG.angstrom ** 2))
        elif moment_type == "Hexadecapole":
            hexadecapole = HexadecapoleMoment(
                **_unpack(match, UREG.debye * UREG.angstrom ** 3)
            )
        else:
            raise AssertionError(f"unsupported moment type: {moment_type}")

        spans += match.spans()

    if not moment_type:
        return

    yield Match(data=Moments(dipole, quadrupole, octapole, hexadecapole), spans=spans)
