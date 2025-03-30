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


class TestGetScript(unittest.TestCase):
    def test_get_script(self):
        pyproject = main.PyProject(scripts={"test": "pkg.mod:func"})
        script = main.get_script(pyproject)
        self.assertIsInstance(script, main.Script)
        self.assertEqual(script, main.Script("test", "pkg.mod:func"))

    def test_get_script_returns_none(self):
        pyproject = main.PyProject()
        script = main.get_script(pyproject)
        self.assertIsNone(script)

    def test_get_script_raises_error(self):
        pyproject = main.PyProject(scripts={"one": "pkg.mod:one", "two": "pkg.mod:two"})

        with self.assertRaises(main.PyProjectError) as error:
            main.get_script(pyproject)

        expected = "pyproject.toml has multiple entries in project.scripts section"
        self.assertEqual(error.exception.msg, expected)


class TestUpdateFromPyproject(unittest.TestCase):
    def test_update_from_pyproject(self):
        args = main.Args(main.CURRENT_DIR, main.BUILD_DIR)
        main.update_from_pyproject(args)
        self.assertNotEqual(args.output, main.DEFAULT_OUTPUT)
        self.assertIsNotNone(args.main)

    def test_update_from_pyproject_when_file_is_missing(self):
        with tempfile.TemporaryDirectory() as path:
            temp = pathlib.Path(path).resolve()
            args = main.Args(temp, main.BUILD_DIR)
            main.update_from_pyproject(args)

        self.assertEqual(args.output, main.DEFAULT_OUTPUT)
        self.assertIsNone(args.main)

    def test_update_from_pyproject_without_scripts(self):
        with tempfile.TemporaryDirectory() as path:
            temp = pathlib.Path(path).resolve()
            pyproject = temp / "pyproject.toml"
            pyproject.touch()
            args = main.Args(temp, main.BUILD_DIR)
            main.update_from_pyproject(args)

        self.assertEqual(args.output, main.DEFAULT_OUTPUT)
        self.assertIsNone(args.main)
