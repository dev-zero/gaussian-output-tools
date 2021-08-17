from dataclasses import dataclass
from decimal import Decimal
from math import ceil
from typing import Iterator, List, Optional

import numpy as np
import numpy.typing as npt
import regex as re

from . import UREG, Match

FREQUENCY_MATCH = re.compile(
    r"""
^\ Harmonic\ frequencies [^:]+:\n
(?:
  (?:\ *(?P<colnr>\d+))+\n
  (?:\ *(?P<name>\S+))+\n
  \ Frequencies \ +--(?:\s+(?P<freq>\S+)){1,3}\n
  \ Red\.\ masses\ +--(?:\s+(?P<mass>\S+)){1,3}\n
  \ Frc\ consts  \ +--(?:\s+(?P<frcc>\S+)){1,3}\n
  \ IR\ Inten    \ +--(?:\s+(?P<intens>\S+)){1,3}\n
  \ +Atom.+\n
  # the quantifier {3,} avoids that an index line after a normal coordinates
  # line is matched, which would prevent the whole block from being matched again.
  # E.g. we are exploiting that there are a min number of 5 numbers in normal coords
  # row, but at max 3 numbers in an index row:
  (?:\ + (?P<idx>\d+) \ + (?P<an>\d+) \ + (?:\ +(?P<coord>\S+)){3,}\n)+
)+
""",
    re.VERBOSE | re.MULTILINE,
)


@dataclass
class Frequencies:
    freqs: List[Decimal]
    red_masses: List[Decimal]
    force_constants: List[Decimal]
    ir_intensities: List[Decimal]
    atomic_numbers: List[int]
    names: List[str]
    normal_coords: npt.NDArray


def match_frequencies(
    content: str, start: Optional[int] = None, end: Optional[int] = None
) -> Iterator[Match]:
    for match in FREQUENCY_MATCH.finditer(content, start, end):
        natoms = max(int(n) for n in match.captures("idx"))
        ncols = int(
            match["colnr"]
        )  # get the last colnr, which is equal the number of frequencies
        # the capture contains a list of all atom indexes (repeated in each column):
        normal_coords = np.empty((ncols, natoms, 3))

        nblocks = ceil(ncols / 3)
        coords = match.captures("coord")
        for block in range(0, nblocks):
            nbcols = min(3, ncols - block * 3)
            for col in range(0, nbcols):
                for row in range(natoms):
                    idx = row * 3 * nbcols + block * 9 * natoms + 3 * col
                    normal_coords[col + 3 * block, row, :] = [
                        Decimal(d) for d in coords[idx : idx + 3]
                    ]

        yield Match(
            data=Frequencies(
                [Decimal(v) * UREG.cm ** -1 for v in match.captures("freq")],
                [Decimal(v) * UREG.u for v in match.captures("mass")],
                [
                    Decimal(v) * UREG.millidyne / UREG.angstrom
                    for v in match.captures("frcc")
                ],
                [
                    Decimal(v) * UREG.kilometer / UREG.mole
                    for v in match.captures("intens")
                ],
                [int(a) for a in match.captures("an")[:natoms]],
                match.captures("name"),
                normal_coords,
            ),
            spans=match.spans(),
        )
