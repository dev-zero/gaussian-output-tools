import re
from itertools import chain

import click
from rich.console import Console
from rich.highlighter import RegexHighlighter, ReprHighlighter

from .blocks import merged_spans
from .blocks.dipole import match_dipole
from .blocks.frequencies import match_frequencies
from .blocks.moments import match_moments
from .blocks.parameters import match_parameters
from .blocks.scf import match_scf

STEP_MATCH = re.compile(r"^ -+\n #(?P<settings>.+?)\n -+\n", re.MULTILINE | re.DOTALL)


class FortranNumberHighlighter(RegexHighlighter):
    base_style = "repr."
    highlights = ReprHighlighter.highlights + [
        r"(?P<number>[\+\-]?(\d*[\.]\d+|\d+[\.]?\d*)([DEe][\+\-]?\d+)?)"
    ]


@click.command()
@click.argument("fhandle", metavar="[FILE|-]", type=click.File(), default="-")
@click.option(
    "--color",
    type=click.Choice(("auto", "always")),
    default="auto",
    help="When to colorize output",
)
@click.option(
    "--format",
    "oformat",
    type=click.Choice(("highlight", "objects")),
    default="highlight",
    help=(
        "What to output: 'highlight' gives the input with matched parts highlighted,"
        " 'objects' pretty prints the resulting objects"
    ),
)
def g16parse(fhandle, color, oformat):
    """Parse the Gaussian output FILE and return a structured output"""
    console = Console(
        force_terminal=True if color == "always" else None,
        highlighter=FortranNumberHighlighter(),
    )

    content = fhandle.read()

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

    for step_idx, (step_config, step_start, step_end) in enumerate(
        zip(step_configs, step_starts, step_ends)
    ):
        if oformat == "objects":
            console.rule(f"[bold red]STEP {step_idx}: {step_config}")

        for match in chain(
            match_scf(content, step_start, step_end),
            match_moments(content, step_start, step_end),
            match_parameters(content, step_start, step_end),
            match_dipole(content, step_start, step_end),
            match_frequencies(content, step_start, step_end),
        ):
            spans += match.spans
            if oformat == "objects":
                console.print(match.data)

    if oformat == "highlight":
        spans = merged_spans(spans)

        ptr = 0
        for start, end in spans:
            console.print(
                f"[dim]{content[ptr:start]}[/dim][bold]{content[start:end]}[/bold]",
                end="",
            )
            ptr = end

        console.print(f"[dim]{content[ptr:]}[/dim]")
