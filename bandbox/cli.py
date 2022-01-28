import argparse
import shlex
import sys

parser = argparse.ArgumentParser(prog='bandbox', description="Diagnose disorganised data file/folders")
# parser.add_argument('path', default='.', help="path to diagnose [default: '.']")
# parser.add_argument('-p', '--prefix', default='', help="prefix to exclude [default: '']")
# parser.add_argument('-d', '--display-paths', default=False, action='store_true',
#                     help="display all the directories found [default: False]")
# parser.add_argument('-i', '--input-data', help="input data from a file")
# parser.add_argument('--hide-file-counts', default=True, action='store_false',
#                     help="display file counts [default: True]")

subparsers = parser.add_subparsers(dest='command', title='Commands available')

# analyse
analyse_parser = subparsers.add_parser(
    'analyse',
    description='analyse the data tree',
    help='analyse the data tree',
)

# view
view_parser = subparsers.add_parser(
    'view',
    description='display the data tree',
    help='display the data tree'
)
view_parser.add_argument('path', default='.', help="path to diagnose [default: '.']")
view_parser.add_argument('-p', '--prefix', default='', help="prefix to exclude [default: '']")
view_parser.add_argument('-d', '--display-paths', default=False, action='store_true',
                    help="display all the directories found [default: False]")
view_parser.add_argument('-i', '--input-data', help="input data from a file")
view_parser.add_argument('--hide-file-counts', default=True, action='store_false',
                    help="display file counts [default: True]")

def parse_args():
    """Parse CLI args"""
    args = parser.parse_args()
    return args


def cli(cmd):
    """CLI standin"""
    sys.argv = shlex.split(cmd)
    return parse_args()
