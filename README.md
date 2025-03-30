# pkging

Build a single executable file of your Python program.

Python supports the direct execution of Python code inside zip files. _pkging_ uses Python's built-in module [zipapp](https://docs.python.org/3/library/zipapp.html), bundling all dependencies inside the generated package, allowing easy distribution of software and dependency isolation.
