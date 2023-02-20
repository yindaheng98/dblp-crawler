import argparse
import importlib


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
    pid_list, journal_list = [], []
    for pid_s in args.__getattribute__(pid_dest):
        try:
            pid = eval(pid_s)
            if isinstance(pid, str):
                pid_list.append(pid)
            else:
                pid_list.extend(pid)
        except:
            pid_list.append(pid_s)
    for journal_s in args.__getattribute__(journal_dest):
        try:
            journal = eval(journal_s)
            if isinstance(journal, str):
                journal_list.append(journal)
            else:
                journal_list.extend(journal)
        except:
            journal_list.append(journal_s)
    return pid_list, journal_list
