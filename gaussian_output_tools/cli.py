import re
from itertools import chain

import click

from .blocks import merged_spans
from .blocks.dipole import match_dipole
from .blocks.frequencies import match_frequencies
from .blocks.moments import match_moments
from .blocks.parameters import match_parameters
from .blocks.scf import match_scf

STEP_MATCH = re.compile(r"^ -+\n #(?P<settings>.+)\n -+\n", re.MULTILINE)


@click.command()
@click.argument("fhandle", metavar="[FILE|-]", type=click.File(), default="-")
@click.option(
    "--color",
    "color",
    type=click.Choice(("auto", "always")),
    default="auto",
    help="When to colorize output",
)
def g16parse(fhandle, color):
    """Parse the Gaussian output FILE and return a structured output"""

    content = fhandle.read()

    step_configs = []
    step_starts = []
    step_ends = []
    spans = []

    for match in STEP_MATCH.finditer(content):
        step_configs.append(match["settings"])
        step_ends.append(match.span()[0])
        step_starts.append(match.span()[1] + 1)
        spans.append(match.span())
    del step_ends[0]
    step_ends.append(len(content))

    for step_start, step_end in zip(step_starts, step_ends):
        for match in chain(
            match_scf(content, step_start, step_end),
            match_moments(content, step_start, step_end),
            match_parameters(content, step_start, step_end),
            match_dipole(content, step_start, step_end),
            match_frequencies(content, step_start, step_end),
        ):
            spans += match.spans

    spans = merged_spans(spans)

    ptr = 0
    for start, end in spans:
        click.secho(
            content[ptr:start],
            nl=False,
            dim=True,
            color=None if color == "auto" else True,
        )
        click.secho(
            content[start:end],
            nl=False,
            bold=True,
            color=None if color == "auto" else True,
        )
        ptr = end
    click.secho(
        content[ptr:], nl=False, dim=True, color=None if color == "auto" else True
    )
