import argparse
import dataclasses
import pathlib
import shutil
import subprocess
import sys
import tempfile
import typing
import zipapp

from pkging import __appname__, __version__

try:
    import tomllib  # pyright: ignore
except ImportError:
    import tomli as tomllib


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


@dataclasses.dataclass
class PyProject:
    scripts: typing.Optional[dict[str, str]] = None


class Script(typing.NamedTuple):
    name: str
    value: str


class PyProjectError(Exception):
    def __init__(self, msg: str) -> None:
        super().__init__()
        self.msg = msg


def load_pyproject(path: pathlib.Path) -> typing.Optional[PyProject]:
    pyproject = path / "pyproject.toml"

    if not pyproject.exists():
        return None

    with pyproject.open("rb") as file:
        toml = tomllib.load(file)

    project = toml.get("project", {})
    return PyProject(scripts=project.get("scripts"))


def get_script(pyproject: PyProject) -> typing.Optional[Script]:
    if pyproject.scripts is None:
        return None

    if len(pyproject.scripts) != 1:
        raise PyProjectError("pyproject.toml has multiple entries in project.scripts section")

    for key, value in pyproject.scripts.items():
        return Script(key, value)


def update_from_pyproject(args: Args) -> None:
    pyproject = load_pyproject(args.source)

    if pyproject is None:
        return None

    script = get_script(pyproject)

    if script is None:
        return None

    if args.output == DEFAULT_OUTPUT:
        args.output = script.name

    if args.main is None:
        args.main = script.value


def run(*cmd: str) -> str:
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    if result.returncode != 0:
        error = result.stdout.decode()
        sys.exit(error)

    return result.stdout.decode()


def pip(source: pathlib.Path, target: pathlib.Path) -> str:
    src = str(source)
    dst = str(target)
    cmd = ["pip", "install", "--disable-pip-version-check", "--no-compile", "--target", dst, src]
    return run(*cmd)


def clean(path: pathlib.Path) -> None:
    dirs = ["bin"]

    for dir in (path / d for d in dirs):
        if dir.exists():
            shutil.rmtree(dir)


def pack(
    source: pathlib.Path,
    target: pathlib.Path,
    name: str,
    interpreter: str = DEFAULT_INTERPRETER,
    main: typing.Optional[str] = None,
) -> None:
    target.mkdir(parents=True, exist_ok=True)
    target = target / name
    zipapp.create_archive(source, target, interpreter=interpreter, main=main)


def build(args: Args) -> None:
    with tempfile.TemporaryDirectory() as path:
        temp = pathlib.Path(path).resolve()
        pip(args.source, temp)
        clean(temp)
        pack(temp, args.target, args.output, args.interpreter, args.main)


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
