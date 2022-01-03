import re
from dataclasses import dataclass
from itertools import chain
from typing import Iterator, List, Union

from .blocks import Match
from .blocks.dipole import match_dipole
from .blocks.frequencies import match_frequencies
from .blocks.moments import match_moments
from .blocks.orientation import match_orientation
from .blocks.parameters import match_parameters
from .blocks.scf import match_scf

STEP_MATCH = re.compile(r"^ -+\n #(?P<settings>.+?)\n -+\n", re.MULTILINE | re.DOTALL)


@dataclass
class Step:
    settings: str
    data: Union[List[Match], Iterator[Match]]


def parse_iter(content: str) -> Iterator[Step]:
    step_configs = []
    step_starts = []
    step_ends = []
    spans = []

    for match in STEP_MATCH.finditer(content):
        step_configs.append(match["settings"].replace("\n ", ""))
        step_ends.append(match.span()[0])
        step_starts.append(match.span()[1] + 1)
        spans.append(match.span())
    del step_ends[0]
    step_ends.append(len(content))

    for step_config, step_start, step_end in zip(step_configs, step_starts, step_ends):
        yield Step(
            step_config,
            chain(
                match_scf(content, step_start, step_end),
                match_moments(content, step_start, step_end),
                match_parameters(content, step_start, step_end),
                match_orientation(content, step_start, step_end),
                match_dipole(content, step_start, step_end),
                match_frequencies(content, step_start, step_end),
            ),
        )


def parse_all(content: str) -> List[Step]:
    return [Step(step.settings, list(step.data)) for step in parse_iter(content)]
