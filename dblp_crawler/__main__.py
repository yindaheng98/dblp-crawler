import argparse
from typing import Iterable

from dblp_crawler import Publication
from dblp_crawler.keyword.arg import add_argument as add_argument_kw, parse_args as parse_args_kw
from dblp_crawler.arg import add_argument_pid, add_argument_journal, parse_args_pid_journal
from dblp_crawler.summarizer.networkx import NetworkxGraph
from dblp_crawler.summarizer.neo4j import Neo4jGraph


class NetworkxGraphDefault(NetworkxGraph):
    def __init__(self, keywords, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.keywords = keywords

    def filter_publications_at_crawler(self, publications: Iterable[Publication]) -> Iterable[Publication]:
        yield from publications

    def filter_publications_at_output(self, publications: Iterable[Publication]) -> Iterable[Publication]:
        yield from publications


class Neo4jGraphDefault(Neo4jGraph):
    def __init__(self, keywords, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.keywords = keywords

    def filter_publications_at_crawler(self, publications: Iterable[Publication]) -> Iterable[Publication]:
        yield from publications

    def filter_publications_at_output(self, publications: Iterable[Publication]) -> Iterable[Publication]:
        yield from publications


parser = argparse.ArgumentParser()

add_argument_kw(parser)
add_argument_pid(parser)
add_argument_journal(parser)


def func_parser(parser):
    keywords = parse_args_kw(parser)
    pid_list, journal_list = parse_args_pid_journal(parser)
    print(keywords.rules)
    print(pid_list)
    print(journal_list)
    return keywords, pid_list, journal_list


subparsers = parser.add_subparsers(help='sub-command help')

parser_nx = subparsers.add_parser('networkx', help='networkx help')
parser_nx.add_argument("--dest", type=str, required=True, help=f'Set dest.')


def func_parser_nx(parser):
    keywords, pid_list, journal_list = func_parser(parser)
    args = parser.parse_args()
    dest = args.dest
    print(dest)


parser_nx.set_defaults(func=func_parser_nx)

parser_n4j = subparsers.add_parser('neo4j', help='neo4j help')
parser_n4j.add_argument("--auth", type=str, required=True, help=f'Set auth.')
parser_n4j.add_argument("--uri", type=str, required=True, help=f'Set uri.')


def func_parser_n4j(parser):
    keywords, pid_list, journal_list = func_parser(parser)
    args = parser.parse_args()
    auth = args.auth
    uri = args.uri
    print(auth, uri)


parser_n4j.set_defaults(func=func_parser_n4j)

args = parser.parse_args()
args.func(parser)
