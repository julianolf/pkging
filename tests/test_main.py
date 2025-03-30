import io
import pathlib
import sys
import tempfile
import unittest
import zipapp
from unittest import mock

from pkging import __appname__, __version__, main

try:
    import tomllib  # pyright: ignore
except ImportError:
    import tomli as tomllib


class TestParseArgs(unittest.TestCase):
    @mock.patch.object(sys, "argv", ["pkging"])
    def test_parser(self):
        args = main.parse_args()
        self.assertIsInstance(args, main.Args)
        self.assertEqual(args.source, main.CURRENT_DIR)
        self.assertEqual(args.target, main.BUILD_DIR)
        self.assertEqual(args.output, main.DEFAULT_OUTPUT)
        self.assertEqual(args.interpreter, main.DEFAULT_INTERPRETER)
        self.assertIsNone(args.main)

    @mock.patch.multiple(sys, argv=["pkging", "--version"], stdout=io.StringIO())
    def test_parser_show_version_and_exit(self):
        with self.assertRaises(SystemExit):
            main.parse_args()

        expected = f"{__appname__} {__version__}"
        output = sys.stdout.getvalue().strip()  # pyright: ignore
        self.assertEqual(expected, output)


class TestLoadPyproject(unittest.TestCase):
    def test_returning_pyproject(self):
        pyproject = main.load_pyproject(main.CURRENT_DIR)
        self.assertIsInstance(pyproject, main.PyProject)

    def test_returning_none_when_file_is_missing(self):
        with tempfile.TemporaryDirectory() as path:
            temp = pathlib.Path(path).resolve()
            pyproject = main.load_pyproject(temp)

        self.assertIsNone(pyproject)


class TestGetScript(unittest.TestCase):
    def test_returning_script(self):
        pyproject = main.PyProject(scripts={"test": "pkg.mod:func"})
        script = main.get_script(pyproject)
        self.assertIsInstance(script, main.Script)
        self.assertEqual(script, main.Script("test", "pkg.mod:func"))

    def test_returning_none(self):
        pyproject = main.PyProject()
        script = main.get_script(pyproject)
        self.assertIsNone(script)

    def test_raising_error(self):
        pyproject = main.PyProject(scripts={"one": "pkg.mod:one", "two": "pkg.mod:two"})

        with self.assertRaises(main.PyProjectError) as error:
            main.get_script(pyproject)

        expected = "pyproject.toml has multiple entries in project.scripts section"
        self.assertEqual(error.exception.msg, expected)


class TestUpdateFromPyproject(unittest.TestCase):
    def test_updating_args(self):
        args = main.Args(main.CURRENT_DIR, main.BUILD_DIR)
        main.update_from_pyproject(args)
        self.assertNotEqual(args.output, main.DEFAULT_OUTPUT)
        self.assertIsNotNone(args.main)

    def test_nothing_changes_when_file_is_missing(self):
        with tempfile.TemporaryDirectory() as path:
            temp = pathlib.Path(path).resolve()
            args = main.Args(temp, main.BUILD_DIR)
            main.update_from_pyproject(args)

        self.assertEqual(args.output, main.DEFAULT_OUTPUT)
        self.assertIsNone(args.main)

    def test_nothing_changes_without_scripts(self):
        with tempfile.TemporaryDirectory() as path:
            temp = pathlib.Path(path).resolve()
            pyproject = temp / "pyproject.toml"
            pyproject.touch()
            args = main.Args(temp, main.BUILD_DIR)
            main.update_from_pyproject(args)

        self.assertEqual(args.output, main.DEFAULT_OUTPUT)
        self.assertIsNone(args.main)


class TestRun(unittest.TestCase):
    def test_run_command(self):
        expected = "test\n"
        command = ("python", "-c", "print('test')")
        self.assertEqual(main.run(*command), expected)

    def test_exit_program_on_errors(self):
        command = ("python", "-c", "print 'test'")
        with self.assertRaises(SystemExit):
            main.run(*command)


class TestPip(unittest.TestCase):
    @mock.patch.object(main, "run")
    def test_pip(self, run):
        main.pip(main.CURRENT_DIR, main.BUILD_DIR)
        expected = mock.call(
            "pip",
            "install",
            "--disable-pip-version-check",
            "--no-compile",
            "--target",
            str(main.BUILD_DIR),
            str(main.CURRENT_DIR),
        )
        self.assertEqual(run.call_args, expected)


class TestClean(unittest.TestCase):
    def test_clean(self):
        with tempfile.TemporaryDirectory() as path:
            temp = pathlib.Path(path).resolve()

            bin = temp / "bin"
            bin.mkdir()
            self.assertTrue(bin.exists())

            main.clean(temp)
            self.assertFalse(bin.exists())


class TestPack(unittest.TestCase):
    def test_pack(self):
        with tempfile.TemporaryDirectory() as path:
            temp = pathlib.Path(path).resolve()

            source = temp / "source"
            source.mkdir()

            entrypoint = source / "__main__.py"
            entrypoint.touch()

            target = temp / "build"
            name = "test"

            main.pack(source, target, name)

            expected = target / name
            self.assertTrue(expected.exists())


class TestBuild(unittest.TestCase):
    @mock.patch.object(main, "pack")
    @mock.patch.object(main, "clean")
    @mock.patch.object(main, "pip")
    def test_build(self, pip, clean, pack):
        args = main.Args(main.CURRENT_DIR, main.BUILD_DIR)
        main.build(args)
        self.assertTrue(pip.called)
        self.assertTrue(clean.called)
        self.assertTrue(pack.called)


class TestErrorHandler(unittest.TestCase):
    def test_without_errors(self):
        @main.error_handler
        def func():
            pass

        self.assertIsNone(func())

    def test_handling_errors(self):
        errors = [
            zipapp.ZipAppError(),
            tomllib.TOMLDecodeError(msg="", doc="", pos=0),
            main.PyProjectError(""),
        ]

        for error in errors:
            with self.subTest(error_type=type(error)):

                def func(error=error):
                    raise error

                with self.assertRaises(SystemExit):
                    main.error_handler(func)()
