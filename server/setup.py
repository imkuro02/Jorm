from pathlib import Path

from setuptools import setup, Extension
from Cython.Build import cythonize


ROOT = Path(__file__).resolve().parent


source_files = [
    path
    for path in ROOT.rglob("*.py")
    if "env" not in path.parts
    and "build" not in path.parts
    and "__pycache__" not in path.parts
    and path.name not in {
        "setup.py",
        "build.py",
        "__init__.py",
    }
]


extensions = []

for path in source_files:
    relative = path.relative_to(ROOT)
    module_name = ".".join(relative.with_suffix("").parts)

    extensions.append(
        Extension(
            module_name,
            [str(path)],
        )
    )


setup(
    ext_modules=cythonize(
        extensions,
        compiler_directives={
            "language_level": 3,
        },
    ),
)
