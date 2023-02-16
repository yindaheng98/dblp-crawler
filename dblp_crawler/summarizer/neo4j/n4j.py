import abc
import asyncio
import logging
from typing import Optional

from neo4j import Session

from dblp_crawler import Graph, DBLPPerson, Publication

logger = logging.getLogger("graph")


def add_person(tx, person: DBLPPerson):
    tx.run("MERGE (a:Person {pid: $pid, name: $name})", pid=person.pid(), name=person.name())


def add_edge(tx, a: str, b: str, publication: Publication):
    tx.run("MATCH (a:Person) WHERE a.pid = $a "
           "MATCH (b:Person) WHERE b.pid = $b "
           "MERGE (p:Publication {key:$key, title:$title, journal_key:$journal_key, journal:$journal, year:$year}) "
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


if __name__ == "__main__":
    import logging
    import random
    from neo4j import GraphDatabase

    logging.basicConfig(level=logging.DEBUG)


    class GG(Neo4jGraph):
        def filter_publications_at_crawler(self, publications):
            publications = list(publications)
            if len(publications) > 0:
                publication = publications[random.randint(0, len(publications) - 1)]
                yield publication

        def filter_publications_at_output(self, publications):
            return self.filter_publications_at_crawler(publications)


    async def main():
        with GraphDatabase.driver("neo4j://10.128.202.18:7687") as driver:
            with driver.session() as session:
                g = GG(session, ['74/1552-1', '256/5272'], [])
                await g.bfs_once()
                print("-" * 100)
                await g.bfs_once()
                print("-" * 100)
                g.summarize()


    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
