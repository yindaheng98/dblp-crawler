import argparse


def add_argument_pid(parser: argparse.ArgumentParser, *flags, dest: str = 'pid') -> None:
    if len(flags) <= 0:
        flags = ['-p', '--pid']
    parser.add_argument(
        *flags, dest=dest, action='append', required=False, default=[],
        help=f'Specified author pids to start crawling.'
    )


def add_argument_journal(parser: argparse.ArgumentParser, *flags, dest: str = 'journal') -> None:
    if len(flags) <= 0:
        flags = ['-j', '--journal']
    parser.add_argument(
        *flags, dest=dest, action='append', required=False, default=[],
        help=f'Specify author journal keys to start crawling.'
    )


def parse_args_pid_journal(parser: argparse.ArgumentParser, pid_dest: str = 'pid', journal_dest: str = 'journal'):
    args = parser.parse_args()
    return args.__getattribute__(pid_dest), args.__getattribute__(journal_dest)
