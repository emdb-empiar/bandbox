import os
import pathlib
import threading
import typing





def scandir_recursive(path: typing.Union[str, pathlib.Path], recursive=True,
                      exclude: typing.Union[None, list] = None) -> typing.Generator:
    """Recursively scan a directory

    Recursion can be switchef off
    """
    with os.scandir(path) as dir_entries:
        for dir_entry in dir_entries:
            if dir_entry.is_dir():
                if os.listdir(dir_entry.path):
                    yield dir_entry
                    if recursive:
                        yield from scandir_recursive(dir_entry.path)
                else:
                    yield dir_entry
            else:
                yield dir_entry
