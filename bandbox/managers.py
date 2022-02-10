import asyncio
import json
import sys

from bandbox import utils
from bandbox.models import Tree


async def _analyse_engines(tree, args):
    """Run engines concurrently"""
    from bandbox import engines
    import inspect
    engines_ = inspect.getmembers(engines, inspect.isfunction)
    awaitables = list()
    for engine_name, engine in engines_:
        if engine_name.startswith('_'):  # skip private methods
            continue
        awaitables.append(engine(tree, args))
    await asyncio.gather(*awaitables)


def analyse(args):
    """Analyse the given dataset"""
    # decide which engines we will include
    # e.g. n2_long_names -> list of entities with long names
    # entry point
    dir_entries = utils.scandir_recursive(args.path)
    tree = Tree.from_data(dir_entries, prefix=str(args.prefix), show_file_counts=args.hide_file_counts, args=args)
    if args.show_tree:
        print(tree)
    if sys.version_info.minor > 6:  # 3.7+
        asyncio.run(_analyse_engines(tree, args))
    else:  # python 3.6
        loop = asyncio.get_event_loop()
        loop.run_until_complete(_analyse_engines(tree, args))
        loop.close()


def view(args):
    """View the given dataset"""
    if args.input_file:
        with open(args.input_file) as f:
            data = f.read().strip().split(', ')
    else:
        data = utils.scandir_recursive(args.path)
    tree = Tree.from_data(data, prefix=str(args.path.parent), show_file_counts=args.hide_file_counts, args=args)
    if args.verbose:
        print(f"info: displaying nested tree data...", file=sys.stderr)
        print(json.dumps(tree.data, indent=4), file=sys.stderr)
    try:
        print(tree)
    except BrokenPipeError:
        pass
