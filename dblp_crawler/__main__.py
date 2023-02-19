import argparse
import asyncio
from typing import Iterable

from dblp_crawler import Publication
from dblp_crawler.keyword import Keywords
from dblp_crawler.keyword.arg import add_argument as add_argument_kw, parse_args as parse_args_kw
from dblp_crawler.arg import add_argument_pid, add_argument_journal, parse_args_pid_journal
from dblp_crawler.summarizer.networkx import NetworkxGraph
from dblp_crawler.summarizer.neo4j import Neo4jGraph

parser = argparse.ArgumentParser()

parser.add_argument("-y", "--year", type=int, help="Set year.", required=True)
add_argument_kw(parser)
add_argument_pid(parser)
add_argument_journal(parser)


def func_parser(parser):
    args = parser.parse_args()
    year = args.year
    keywords = parse_args_kw(parser)
    pid_list, journal_list = parse_args_pid_journal(parser)
    print(keywords.rules)
    print(pid_list)
    print(journal_list)
    return year, keywords, pid_list, journal_list


def filter_publications_at_crawler(publications, year: int, keywords: Keywords):
    for publication in publications:
        if publication.year() >= year and keywords.match_words(publication.title()):
            yield publication


def filter_publications_at_output(publications, keywords: Keywords):
    for publication in publications:
        if keywords.match(publication.title()):
            yield publication


async def bfs_to_end(graph, limit: int = 0):
    while min(*(await graph.bfs_once())) > 0 and (limit != 0):
        print("Still running......")
        limit -= 1


subparsers = parser.add_subparsers(help='sub-command help')


# --------- for NetworkxGraph ---------

class NetworkxGraphDefault(NetworkxGraph):
    def __init__(self, year, keywords, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.year = year
        self.keywords = keywords

    def filter_publications_at_crawler(self, publications: Iterable[Publication]) -> Iterable[Publication]:
        yield from filter_publications_at_crawler(publications, self.year, self.keywords)

    def filter_publications_at_output(self, publications: Iterable[Publication]) -> Iterable[Publication]:
        yield from filter_publications_at_output(publications, self.keywords)


parser_nx = subparsers.add_parser('networkx', help='networkx help')
parser_nx.add_argument("--dest", type=str, required=True, help=f'Set dest.')


def func_parser_nx(parser):
    year, keywords, pid_list, journal_list = func_parser(parser)
    args = parser.parse_args()
    dest = args.dest
    print(dest)
    g = NetworkxGraphDefault(year=year, keywords=keywords, pid_list=pid_list, journal_list=journal_list)
    asyncio.get_event_loop().run_until_complete(bfs_to_end(g))
    g = g.graph_summary()
    summary = dict(
        nodes=[
            {'id': k, 'label': d['person'].name(), 'data': d}
            for k, d in g.nodes(data=True)
        ],
        edges=[
            {'from': u, 'to': v, 'data': d}
            for u, v, d in g.edges(data=True)
        ]
    )

    import json
    from dblp_crawler import DBLPPerson

    class JSONEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, DBLPPerson):
                return obj.pid() + "\n" + str(obj.person())
            if isinstance(obj, Publication):
                return str(obj)
            return json.JSONEncoder.default(self, obj)

    with open(dest, 'w', encoding='utf8') as f:
        json.dump(summary, fp=f, cls=JSONEncoder, indent=2)


parser_nx.set_defaults(func=func_parser_nx)


# --------- for Neo4jGraph ---------


class Neo4jGraphDefault(Neo4jGraph):
    def __init__(self, year, keywords, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.year = year
        self.keywords = keywords

    def filter_publications_at_crawler(self, publications: Iterable[Publication]) -> Iterable[Publication]:
        yield from filter_publications_at_crawler(publications, self.year, self.keywords)

    def filter_publications_at_output(self, publications: Iterable[Publication]) -> Iterable[Publication]:
        yield from filter_publications_at_output(publications, self.keywords)


parser_n4j = subparsers.add_parser('neo4j', help='neo4j help')
parser_n4j.add_argument("--auth", type=str, required=True, help=f'Set auth.')
parser_n4j.add_argument("--uri", type=str, required=True, help=f'Set uri.')


def func_parser_n4j(parser):
    from neo4j import GraphDatabase
    year, keywords, pid_list, journal_list = func_parser(parser)
    args = parser.parse_args()
    auth = args.auth
    uri = args.uri
    print(auth, uri)

    with GraphDatabase.driver(args.uri, auth=args.auth) as driver:
        with driver.session() as session:
            g = Neo4jGraphDefault(
                year=year, keywords=keywords, session=session,
                pid_list=pid_list, journal_list=journal_list)
            asyncio.get_event_loop().run_until_complete(bfs_to_end(g))
            g.summarize()


parser_n4j.set_defaults(func=func_parser_n4j)

# --------- Run ---------
args = parser.parse_args()
args.func(parser)
