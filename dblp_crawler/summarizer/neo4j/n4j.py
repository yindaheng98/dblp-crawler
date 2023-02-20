import abc
import asyncio
import logging
from typing import Optional

from neo4j import Session

from dblp_crawler import Graph, DBLPPerson, Publication

logger = logging.getLogger("graph")


def add_person(tx, person: DBLPPerson):
    tx.run("MERGE (a:Person {pid: $pid, name: $name})", pid=person.pid(), name=person.name())
    for publication in person.publications():
        tx.run("MATCH (a:Person) WHERE a.pid = $pid "
               "MERGE (p:Publication {key:$key, title:$title, journal_key:$journal_key, journal:$journal, year:$year}) "
               "MERGE (a)-[:WRITE]->(p)",
               pid=person.pid(),
               key=publication.key(),
               title=publication.title(),
               journal_key=publication.journal_key() or "",
               journal=publication.journal() or "",
               year=publication.year())


def add_edge(tx, a: str, b: str, publication: Publication):
    tx.run("MATCH (a:Person) WHERE a.pid = $a "
           "MATCH (b:Person) WHERE b.pid = $b "
           "MERGE (p:Publication {key:$key, title:$title, journal_key:$journal_key, journal:$journal, year:$year, selected: true}) "
           "MERGE (a)-[:WRITE]->(p)"
           "MERGE (b)-[:WRITE]->(p)",
           a=a, b=b,
           key=publication.key(),
           title=publication.title(),
           journal_key=publication.journal_key(),
           journal=publication.journal(),
           year=publication.year())


class Neo4jGraph(Graph, metaclass=abc.ABCMeta):
    def __init__(self, session: Session, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session = session

    def summarize_person(self, a: str, person: Optional[DBLPPerson]):  # 构建summary
        if person is not None:
            self.session.execute_write(add_person, person)  # 把作者信息加进图里

    def summarize_publication(self, a: str, b: str, publication: Publication):  # 构建summary
        self.session.execute_write(add_edge, a, b, publication)  # 把边加进图里
