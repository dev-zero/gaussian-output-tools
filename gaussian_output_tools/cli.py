from itertools import chain
import re

import click

from .blocks import merged_spans
from .blocks.moments import match_moments
from .blocks.parameters import match_parameters
from .blocks.dipole import match_dipole


END_MATCH = re.compile(r"^ Normal termination .+\n", re.MULTILINE)


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
    step_contents = []
    ptr = 0

    for match in END_MATCH.finditer(content):
        # the end of this match also marks the end of this
        step_contents.append(content[ptr:match.span(0)[1]])
        ptr = match.span(0)[1]

    for stepnr, content in enumerate(step_contents, start=1):
        spans = []
        print(f"\nSTEP: {stepnr}\n")

        for match in chain(match_moments(content), match_parameters(content), match_dipole(content)):
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
