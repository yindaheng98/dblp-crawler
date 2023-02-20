import argparse
import asyncio
from typing import Iterable
import logging

from dblp_crawler import Publication
from dblp_crawler.keyword import Keywords
from dblp_crawler.keyword.arg import add_argument as add_argument_kw, parse_args as parse_args_kw
from dblp_crawler.arg import add_argument_pid, add_argument_journal, parse_args_pid_journal
from dblp_crawler.summarizer.networkx import NetworkxGraph
from dblp_crawler.summarizer.neo4j import Neo4jGraph

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('dblp_crawler')

parser = argparse.ArgumentParser()

parser.add_argument("-y", "--year", type=int, help="Only crawl the paper after the specified year.", default=2000)
add_argument_kw(parser)
add_argument_pid(parser)
add_argument_journal(parser)


def func_parser(parser):
    args = parser.parse_args()
    year = args.year
    keywords = parse_args_kw(parser)
    pid_list, journal_list = parse_args_pid_journal(parser)
    logger.info(f"Specified keyword rules: {keywords.rules}")
    logger.info(f"Specified pid_list for init: {pid_list}")
    logger.info(f"Specified journal_list for init: {journal_list}")
    return year, keywords, pid_list, journal_list


def filter_publications_at_crawler(publications, keywords: Keywords):
    for publication in publications:
        if keywords.match_words(publication.title()):
            yield publication


def filter_publications_at_output(publications, year: int, keywords: Keywords):
    for publication in publications:
        if publication.year() >= year and keywords.match(publication.title()):
            yield publication


async def bfs_to_end(graph, limit: int = 0):
    while min(*(await graph.bfs_once())) > 0 and (limit != 0):
        logger.info("Still running......")
        limit -= 1


subparsers = parser.add_subparsers(help='sub-command help')


# --------- for NetworkxGraph ---------

class NetworkxGraphDefault(NetworkxGraph):
    def __init__(self, year, keywords, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.year = year
        self.keywords = keywords

    def filter_publications_at_crawler(self, publications: Iterable[Publication]) -> Iterable[Publication]:
        yield from filter_publications_at_crawler(publications, self.keywords)

    def filter_publications_at_output(self, publications: Iterable[Publication]) -> Iterable[Publication]:
        yield from filter_publications_at_output(publications, self.year, self.keywords)


parser_nx = subparsers.add_parser('networkx', help='Write results to a json file.')
parser_nx.add_argument("--dest", type=str, required=True, help=f'Path to write results.')


def func_parser_nx(parser):
    year, keywords, pid_list, journal_list = func_parser(parser)
    args = parser.parse_args()
    dest = args.dest
    logger.info(f"Specified dest: {dest}")
    g = NetworkxGraphDefault(year=year, keywords=keywords, pid_list=pid_list, journal_list=journal_list)
    asyncio.get_event_loop().run_until_complete(bfs_to_end(g))
    summary = g.dict_summary()

    import json

    with open(dest, 'w', encoding='utf8') as f:
        json.dump(summary, fp=f, indent=2)


parser_nx.set_defaults(func=func_parser_nx)


# --------- for Neo4jGraph ---------


class Neo4jGraphDefault(Neo4jGraph):
    def __init__(self, year, keywords, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.year = year
        self.keywords = keywords

    def filter_publications_at_crawler(self, publications: Iterable[Publication]) -> Iterable[Publication]:
        yield from filter_publications_at_crawler(publications, self.keywords)

    def filter_publications_at_output(self, publications: Iterable[Publication]) -> Iterable[Publication]:
        yield from filter_publications_at_output(publications, self.year, self.keywords)


parser_n4j = subparsers.add_parser('neo4j', help='Write result to neo4j database')
parser_n4j.add_argument("--auth", type=str, default=None, help=f'Auth to neo4j database.')
parser_n4j.add_argument("--uri", type=str, required=True, help=f'URI to neo4j database.')


def func_parser_n4j(parser):
    from neo4j import GraphDatabase
    year, keywords, pid_list, journal_list = func_parser(parser)
    args = parser.parse_args()
    logger.info(f"Specified uri and auth: {args.uri} {args.auth}")

    with GraphDatabase.driver(args.uri, auth=args.auth) as driver:
        with driver.session() as session:
            g = Neo4jGraphDefault(
                year=year, keywords=keywords, session=session,
                pid_list=pid_list, journal_list=journal_list)
            asyncio.get_event_loop().run_until_complete(bfs_to_end(g))
            logger.info(f"Summarizing to: {args.uri}")
            g.summarize()


parser_n4j.set_defaults(func=func_parser_n4j)

# --------- Run ---------
args = parser.parse_args()
args.func(parser)
