from os import walk, scandir, system, listdir
from pathlib import Path
from shlex import split as arg_split
from os.path import isfile, isdir, abspath
# NOTE: unused import statements may be used by other modules using os_utils.
from PySide6.QtGui import QGuiApplication
"""Contains the OS utilities needed to interact with the system and programs used for copying the files."""

DEFAULT_PATTERN: tuple = ("*.*",)


def getPathTarget(path: str) -> str:
    return path.rpartition('\\')[-1] if path[-1] != '\\' else path

def getParentDir(path: str) -> str:
    return path.rpartition('\\')[0]


def dirSize(path: str) -> int:
    """Best way to get size of dir. Returns size in bytes of directory specified by `path`."""
    p = Path(path)
    return sum(f.stat().st_size for f in p.rglob('*') if f.is_file())


def fileCounter(path: str, pattern: tuple | list = None, recursive: bool = True) -> int:
    """Fastest Recursive File Counter. Counts all files contained in directory specified by `path`"""
    if pattern and tuple(pattern) != DEFAULT_PATTERN:
        pattern: set = set(pattern)  # get rid of duplicate patterns
        p = Path(path)
        return sum(sum(1 for _ in p.rglob(w)) for w in pattern) if recursive else sum(sum(1 for _ in p.glob(w)) for w in pattern)

    # Faster way without pattern
    return sum(len(f) for _, _, f in walk(path)) if recursive else len([f for f in scandir(path) if f.is_file()])


def joinArgs(split_arg: list | tuple) -> str:
    return f'"{'" "'.join(split_arg)}"'


def selectFileInExplorer(path: str) -> None:
    system(f'explorer /select,"{path}"')


def showDirInExplorer(path: str):
    system(f'explorer "{path}"')


def copyToClipboard(text: str, application_context: QGuiApplication) -> None:
    application_context.clipboard().setText(text)


if __name__ == "__main__":
    pass  # select_file_in_explorer(r"C:\Users\isaac\Google Drive\Programing Projects\Major\easy_copy\test\src1\")
