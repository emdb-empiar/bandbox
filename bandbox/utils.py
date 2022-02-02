import os
import pathlib
import threading
import typing


async def _report(dirs: list, lock: threading.Lock, rule_text: str, fail_text: str = '') -> None:
    """Reporting function"""
    with lock:
        print(rule_text, end=" ")
        if dirs:
            if fail_text:
                print(fail_text)
            else:
                print(f"fail [{len(dirs)} directories]")
            for item in dirs:
                print(f"  * {item}")
        else:
            print(f"ok")


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
