# pkging

![Tests](https://github.com/julianolf/pkging/actions/workflows/ci.yml/badge.svg?event=push)

Create a single executable file from Python programs.

Python supports the direct execution of Python code inside zip files. _pkging_ uses Python's built-in module [zipapp](https://docs.python.org/3/library/zipapp.html), bundling all dependencies inside the generated package, allowing easy distribution of software and dependency isolation.
