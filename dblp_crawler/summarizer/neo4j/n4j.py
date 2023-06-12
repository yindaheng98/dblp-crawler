import abc
import logging
from typing import Optional

from neo4j import Session

from dblp_crawler import Graph, DBLPPerson, Publication

logger = logging.getLogger("graph")

def add_publication(tx, publication):
    n4jset = "MERGE (p:Publication {key:$key}) SET p.title=$title, p.journal_key=$journal_key, p.journal=$journal, p.year=$year"
    if publication.doi():
        n4jset += ", p.doi=$doi"
    tx.run(n4jset,
            key=publication.key(),
            title=publication.title(),
            journal_key=publication.journal_key() or "",
            journal=publication.journal() or "",
            year=publication.year(),
            doi=publication.doi())


def add_person(tx, person: DBLPPerson, added_pubs: set):
    tx.run("MERGE (a:Person {pid: $pid, name: $name})", pid=person.pid(), name=person.name())
    for publication in person.publications():
        if publication.key() in added_pubs:
            continue
        added_pubs.add(publication.key())
        tx.run("MERGE (a:Person {pid: $pid}) "
               "MERGE (p:Publication {key: $key}) "
               "MERGE (a)-[:WRITE]->(p)",
               pid=person.pid(),
               key=publication.key())
        add_publication(tx, publication)


def add_edge(tx, a: str, b: str, publication: Publication):
    tx.run("MERGE (a:Person {pid: $a}) "
           "MERGE (b:Person {pid: $b}) "
           "MERGE (p:Publication {key: $key}) "
           "MERGE (a)-[:WRITE]->(p)"
           "MERGE (b)-[:WRITE]->(p)",
           a=a, b=b,
           key=publication.key())
    add_publication(tx, publication)


class Neo4jGraph(Graph, metaclass=abc.ABCMeta):
    def __init__(self, session: Session, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session = session
        self.added_pubs = set()

    def summarize_person(self, a: str, person: Optional[DBLPPerson]):  # 构建summary
        if person is not None:
            self.session.execute_write(add_person, person, self.added_pubs)  # 把作者信息加进图里

    def summarize_publication(self, a: str, b: str, publication: Publication):  # 构建summary
        self.session.execute_write(add_edge, a, b, publication)  # 把边加进图里
