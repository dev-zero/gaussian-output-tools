from dataclasses import dataclass
from typing import Any, List, Tuple, Union

import pint


@dataclass
class Match:
    data: Any
    spans: List[
        Union[int, Tuple[int, int]]
    ]  # start and end character indices of the matches


def merged_spans(spans: List[Tuple[int, int]]):
    merged = [(-1, -1)]

    for start, end in sorted(spans):
        if (
            start > merged[-1][1]
        ):  # if the new start is after the latest end, add a new span
            merged.append((start, end))
        else:  # if not, keep the current start and replace its end
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))

    del merged[0]
    return merged


# define global unit registry for all blocks
UREG = pint.UnitRegistry()
