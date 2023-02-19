import argparse
from typing import Iterable

from dblp_crawler import Publication
from dblp_crawler.keyword.arg import add_argument as add_argument_kw, parse_args as parse_args_kw
from dblp_crawler.arg import add_argument_pid, add_argument_journal, parse_args_pid_journal
from dblp_crawler.summarizer.networkx import NetworkxGraph
from dblp_crawler.summarizer.neo4j import Neo4jGraph


class NetworkxGraphDefault(NetworkxGraph):

    def filter_publications_at_crawler(self, publications: Iterable[Publication]) -> Iterable[Publication]:
        yield from publications

    def filter_publications_at_output(self, publications: Iterable[Publication]) -> Iterable[Publication]:
        yield from publications


class Neo4jGraphDefault(Neo4jGraph):

    def filter_publications_at_crawler(self, publications: Iterable[Publication]) -> Iterable[Publication]:
        yield from publications

    def filter_publications_at_output(self, publications: Iterable[Publication]) -> Iterable[Publication]:
        yield from publications


parser = argparse.ArgumentParser()

parser.add_argument('--summarizer', choices=['networkx', 'neo4j'], type=str, default='networkx')
add_argument_kw(parser)
add_argument_pid(parser)
add_argument_journal(parser)

keywords = parse_args_kw(parser)
pid_list, journal_list = parse_args_pid_journal(parser)

print(keywords.rules)
print(pid_list)
print(journal_list)
