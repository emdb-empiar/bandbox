import argparse
import configparser
import os
import pathlib
import shlex
import sys
from typing import Union, Iterable, Optional, List

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


class LocalConfigParser(configparser.ConfigParser):
    """String-printable version"""

    def __init__(self, *args, **kwargs):
        super().__init__(
            interpolation=configparser.ExtendedInterpolation(),
            converters={
                'list': self.getlist,
                'tuple': self.gettuple,
                'python': self.getpython,
                'cre': self.getcre,
            }, *args, **kwargs)
        self._filenames = None

    @property
    def filenames(self):
        return self._filenames

    def read(self, filenames: Union[os.PathLike, Iterable[os.PathLike]], encoding: Optional[str] = None) -> None:
        self._filenames = filenames
        super().read(filenames, encoding)

    def __str__(self):
        string = ""
        for section in self.sections():
            string += f"[{section}]\n"
            for option in self[section]:
                string += f"{option} = {self.get(section, option, raw=True)}\n"
            string += "\n"
        return string

    @staticmethod
    def getlist(value):
        """Convert the option value to a list"""
        return list(map(lambda s: s.strip(), value.split(',')))

    @staticmethod
    def gettuple(value):
        """Convert the option value to a tuple"""
        return tuple(map(lambda s: s.strip(), value.split(',')))

    @staticmethod
    def getpython(value):
        """Evaluate the option value as literal Python code"""
        return eval(value)

    @staticmethod
    def getcre(value):
        """Evaluate a compiled regular expression"""
        import re
        return re.compile(value)


parser = argparse.ArgumentParser(prog='bandbox', description="Evaluate how organised your dataset is")

parent_parser = argparse.ArgumentParser(add_help=False)
parent_parser.add_argument('-c', '--config-file',
                           help="oil configs [default: value of BANDBOX_CONFIG environment variable")
parent_parser.add_argument('-v', '--verbose', default=False, action='store_true',
                           help="verbose output to terminal in addition to log files [default: False]")

subparsers = parser.add_subparsers(dest='command', title='Commands available')

# analyse
analyse_parser = subparsers.add_parser(
    'analyse',
    description='analyse the data tree',
    help='analyse the dataset',
    parents=[parent_parser]
)
_add_arg(analyse_parser, path)
analyse_parser.add_argument('--include-root', default=False, action='store_true',
                            help="include the root directory for analysis [default: False]")
_add_arg(analyse_parser, prefix)
analyse_parser.add_argument('-T', '--show-tree', default=False, action='store_true',
                            help="display the tree [default: False]")
SUMMARY_SIZE = 5
analyse_parser.add_argument(
    '-s', '--summarise-size',
    default=SUMMARY_SIZE, type=int,
    help=f"summarise size [default: {SUMMARY_SIZE}]"
)
analyse_parser.add_argument(
    '-S', '--summarise',
    default=False,
    action='store_true',
    help=f"summarise to --summary-size ({SUMMARY_SIZE}) results in each group [default: False]"
)
_add_arg(analyse_parser, hide_file_counts)

# view
view_parser = subparsers.add_parser(
    'view',
    description='display the data tree',
    help='display the data tree',
    parents=[parent_parser]
)
_add_arg(view_parser, path)
_add_arg(view_parser, prefix)
# todo: remove
# view_parser.add_argument('-v', '--verbose', default=False, action='store_true',
#                          help="verbose output which will display all the directories found [default: False]")
view_parser.add_argument('-f', '--input-file', help="input data from a file")
_add_arg(view_parser, hide_file_counts)


def parse_args():
    """Parse CLI args"""
    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        return None
    # config-file
    if args.config_file is None:
        try:
            args.config_file = os.environ['BANDBOX_CONFIG']
        except KeyError:
            print(f"error: no configs found; please set BANDBOX_CONFIG envvar or provide --config-file path",
                  file=sys.stderr)
            print(f"info: copy and modify the config file from https://raw.githubusercontent.com/emdb-empiar/bandbox/master/bandbox.cfg", file=sys.stderr)
            return None
    # read configs
    configs = LocalConfigParser()
    configs.read(args.config_file)
    args._configs = configs
    # the path must exist
    if not args.path.exists():
        print(f"error: invalid path '{args.path}'", file=sys.stderr)
        return None
    return args


def cli(cmd):
    """CLI standin"""
    sys.argv = shlex.split(cmd)
    return parse_args()
