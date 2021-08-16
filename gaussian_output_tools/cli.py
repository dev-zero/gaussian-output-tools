from itertools import chain

import click

from .blocks import merged_spans
from .blocks.moments import match_moments
from .blocks.parameters import match_parameters


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

    spans = []

    content = fhandle.read()

    for match in chain(match_moments(content), match_parameters(content)):
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
