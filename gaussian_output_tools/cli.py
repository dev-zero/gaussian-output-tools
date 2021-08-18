import click
from rich.console import Console
from rich.highlighter import RegexHighlighter, ReprHighlighter

from .blocks import merged_spans
from .parser import parse_iter


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

    spans = []

    for step_idx, step in enumerate(parse_iter(content)):
        if oformat == "objects":
            console.rule(f"[bold red]STEP {step_idx}: {step.settings}")

        for match in step.data:
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
