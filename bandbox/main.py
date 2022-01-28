# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import os
import sys

from bandbox import managers
from bandbox.cli import parse_args
from bandbox.utils import get_gist_data


def main():
    args = parse_args()
    get_gist_data()
    if args.command == 'analyse':
        return managers.analyse(args)
    elif args.command == 'view':
        return managers.view(args)
    return os.EX_OK


if __name__ == '__main__':
    sys.exit(main())
