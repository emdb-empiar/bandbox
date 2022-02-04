import argparse
import pathlib
import shlex
import sys

# options
hide_file_counts = {
    'args': ['--hide-file-counts'],
    'kwargs': dict(
        default=True,
        action='store_false',
        help="display file counts [default: True]"
    )
}
path = {
    'args': ['path'],
    'kwargs': {
        'nargs': '?',
        'default': '',
        'type': pathlib.Path,
        'help': "path to diagnose [default: '.']"
    }
}

prefix = {
    'args': ['-p', '--prefix'],
    'kwargs': {
        'default': '',
        'help': "prefix to exclude [default: '']"
    }
}


def _add_arg(parser_: argparse.ArgumentParser, option: dict):
    """Add options to parser"""
    return parser_.add_argument(*option['args'], **option['kwargs'])


parser = argparse.ArgumentParser(prog='bandbox', description="Evaluate how organised your dataset is")

subparsers = parser.add_subparsers(dest='command', title='Commands available')

# analyse
analyse_parser = subparsers.add_parser(
    'analyse',
    description='analyse the data tree',
    help='analyse the dataset',
)
_add_arg(analyse_parser, path)
analyse_parser.add_argument('--include-root', default=False, action='store_true',
                            help="include the root directory for analysis [default: False]")
_add_arg(analyse_parser, prefix)
analyse_parser.add_argument('--show-tree', default=False, action='store_true', help="display the tree [default: False]")
SUMMARY_SIZE = 5
analyse_parser.add_argument(
    '-s', '--summarise-size',
    default=SUMMARY_SIZE, type=int,
    help=f"summarise size [default: {SUMMARY_SIZE}]"
)
analyse_parser.add_argument(
    '--summarise',
    default=False,
    action='store_true',
    help=f"summarise to --summary-size ({SUMMARY_SIZE}) results in each group [default: False]"
)
_add_arg(analyse_parser, hide_file_counts)

# view
view_parser = subparsers.add_parser(
    'view',
    description='display the data tree',
    help='display the data tree'
)
_add_arg(view_parser, path)
_add_arg(view_parser, prefix)
view_parser.add_argument('-v', '--verbose', default=False, action='store_true',
                         help="verbose output which will display all the directories found [default: False]")
view_parser.add_argument('-f', '--input-file', help="input data from a file")
_add_arg(view_parser, hide_file_counts)


def parse_args():
    """Parse CLI args"""
    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        return None
    # the path must exist
    if not args.path.exists():
        print(f"error: invalid path '{args.path}'", file=sys.stderr)
        return None
    return args


def cli(cmd):
    """CLI standin"""
    sys.argv = shlex.split(cmd)
    return parse_args()
