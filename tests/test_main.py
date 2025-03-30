import io
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

from pkging import __appname__, __version__, main


class TestParseArgs(unittest.TestCase):
    @mock.patch.object(sys, "argv", ["pkging"])
    def test_parse_args(self) -> None:
        args = main.parse_args()
        self.assertIsInstance(args, main.Args)
        self.assertEqual(args.source, main.CURRENT_DIR)
        self.assertEqual(args.target, main.BUILD_DIR)
        self.assertEqual(args.output, main.DEFAULT_OUTPUT)
        self.assertEqual(args.interpreter, main.DEFAULT_INTERPRETER)
        self.assertIsNone(args.main)

    @mock.patch.multiple(sys, argv=["pkging", "--version"], stdout=io.StringIO())
    def test_parse_args_show_version_and_exit(self) -> None:
        with self.assertRaises(SystemExit):
            main.parse_args()

        expected = f"{__appname__} {__version__}"
        output = sys.stdout.getvalue().strip()  # pyright: ignore
        self.assertEqual(expected, output)


class TestLoadPyproject(unittest.TestCase):
    def test_load_pyproject(self):
        pyproject = main.load_pyproject(main.CURRENT_DIR)
        self.assertIsInstance(pyproject, main.PyProject)

    def test_load_pyproject_when_file_is_missing(self):
        with tempfile.TemporaryDirectory() as path:
            temp = pathlib.Path(path).resolve()
            pyproject = main.load_pyproject(temp)

        self.assertIsNone(pyproject)
