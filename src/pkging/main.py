import argparse

from pkging import __appname__, __version__


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog=__appname__,
        description="Build a single executable file of your Python program.",
    )
    parser.add_argument("--version", action="version", version=f"{__appname__} {__version__}")
    return parser.parse_args()


def main() -> None:
    parse_args()
