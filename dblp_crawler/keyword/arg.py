import argparse
import importlib
from . import Keywords


def add_argument(parser: argparse.ArgumentParser, *flags, dest: str = 'keyword') -> None:
    if len(flags) <= 0:
        flags = ['-k', '--keyword']
    parser.add_argument(
        *flags, dest=dest, action='append', required=False, default=[],
        help=f'Specify keyword rules.'
    )


def parse_args(parser: argparse.ArgumentParser, dest: str = 'keyword'):
    args = parser.parse_args()
    keywords = Keywords()
    for s in args.__getattribute__(dest):
        try:
            s = eval(s)
            if isinstance(s, str):
                keywords.add_rule(s)
            else:
                keywords.add_rule(*s)
        except:
            keywords.add_rule(s)
    return keywords
