import asyncio
import json
import random
import sys

from bandbox.core import Tree
from bandbox import utils
from threading import Lock


async def _analyse_engines(tree, lock, args):
    """Run engines concurrently"""
    from bandbox import engines
    import inspect
    engines_ = inspect.getmembers(engines, inspect.isfunction)
    awaitables = list()
    for engine_name, engine in engines_:
        print(engine_name)
        awaitables.append(engine(tree, lock, args))
    await asyncio.gather(*awaitables)


def analyse(args):
    """Analyse the given dataset"""
    # decide which engines we will include
    # e.g. n2_long_names -> list of entities with long names
    # entry point
    lock = Lock()
    dir_entries = utils.scandir_recursive(args.path)
    tree = Tree.from_data(dir_entries, prefix=str(args.path.parent))
    asyncio.run(_analyse_engines(tree, lock, args))


def view(args):
    """View the given dataset"""
    import glob, pathlib, os
    if args.input_file:
        with open(args.input_file) as f:
            data = f.read().strip().split(', ')
    else:
        data = utils.scandir_recursive(args.path)
    tree = Tree.from_data(data, prefix=str(args.path.parent), show_file_counts=args.hide_file_counts)
    if args.verbose:
        print(f"info: displaying nested tree data...", file=sys.stderr)
        print(json.dumps(tree.data, indent=4), file=sys.stderr)
    try:
        print(tree)
    except BrokenPipeError:
        pass



