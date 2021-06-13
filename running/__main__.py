#!/usr/env/bin python3
import logging
import argparse

from running.__version__ import __VERSION__
from running import fillin

logger = logging.getLogger(__name__)


def setup_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="change logging level to DEBUG")               
    parser.add_argument("--version", action="version",
                        version="running {}".format(__VERSION__))
    subparsers = parser.add_subparsers()
    fillin.setup_parser(subparsers)
    return parser


def main():
    parsers = setup_parser()
    args = vars(parsers.parse_args())

    # Config root logger
    if args.get("verbose") == True:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    logging.basicConfig(
        format="[%(levelname)s] %(asctime)s %(filename)s:%(lineno)d %(message)s",
        level=log_level)

    if fillin.run(args):
        pass
    else:
        parsers.print_help()


if __name__ == "__main__":
    main()