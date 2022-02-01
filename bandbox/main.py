import os
import sys

from bandbox import managers
from bandbox.cli import parse_args


def main():
    args = parse_args()
    if args.command == 'analyse':
        return managers.analyse(args)
    elif args.command == 'view':
        return managers.view(args)
    return os.EX_OK


if __name__ == '__main__':
    sys.exit(main())
