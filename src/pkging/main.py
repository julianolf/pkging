import argparse
import dataclasses
import pathlib
import typing

from pkging import __appname__, __version__

CURRENT_DIR = pathlib.Path(".").resolve()
BUILD_DIR = CURRENT_DIR / "build"
DEFAULT_OUTPUT = "obj"
DEFAULT_INTERPRETER = "/usr/bin/env python3"


@dataclasses.dataclass
class Args:
    source: pathlib.Path
    target: pathlib.Path
    output: str = DEFAULT_OUTPUT
    interpreter: str = DEFAULT_INTERPRETER
    main: typing.Optional[str] = None


def parse_args() -> Args:
    parser = argparse.ArgumentParser(
        prog=__appname__,
        description="Build a single executable file of your Python program.",
    )
    parser.add_argument(
        "--source",
        type=pathlib.Path,
        default=CURRENT_DIR,
        help="source directory (default: %(default)s)",
    )
    parser.add_argument(
        "--target",
        type=pathlib.Path,
        default=BUILD_DIR,
        help="target directory (default: %(default)s)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=DEFAULT_OUTPUT,
        help="the name for the executable (default: %(default)s)",
    )
    parser.add_argument(
        "--interpreter",
        type=str,
        default=DEFAULT_INTERPRETER,
        help="the Python interpreter with which the archive will be executed (default: %(default)s)",  # noqa: E501
    )
    parser.add_argument(
        "--main",
        type=str,
        help="the name of a callable which will be used as the main program",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"{__appname__} {__version__}",
    )
    args = parser.parse_args()

    return Args(
        source=args.source.resolve(),
        target=args.target.resolve(),
        output=args.output,
        interpreter=args.interpreter,
        main=args.main,
    )


def main() -> None:
    parse_args()
