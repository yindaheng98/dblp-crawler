import argparse
from . import Keywords


def add_argument(parser: argparse.ArgumentParser, *flags, dest: str = 'keyword', required=True) -> None:
    if len(flags) <= 0:
        flags = ['-k', '--keyword']
    parser.add_argument(
        *flags, dest=dest, action='append', required=required,
        help=f'Set keywords.'
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
