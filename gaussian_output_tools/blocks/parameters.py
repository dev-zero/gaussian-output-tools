from dataclasses import dataclass
from decimal import Decimal
from typing import Iterator, List, Optional, Tuple, TypeVar, Union

import regex as re

from . import Match

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


_T = TypeVar("ParameterEntry")


@dataclass
class ParameterEntry:
    name: str
    definition: str
    value: Decimal
    derivative_info: Union[Tuple[str, Decimal], str]

    @classmethod
    def from_match(cls, name, definition, value, derivinfo) -> _T:
        try:
            deriv, val = derivinfo.split("=")
            derivinfo = (deriv.strip(), Decimal(val))
        except ValueError:
            pass

        return cls(name, definition, Decimal(value), derivinfo)


@dataclass
class Parameters:
    type: str
    entries: List[ParameterEntry]


def match_parameters(
    content: str, start: Optional[int] = None, end: Optional[int] = None
) -> Iterator[Parameters]:
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
