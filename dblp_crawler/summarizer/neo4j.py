import abc
import logging
from typing import Optional

from neo4j import Session

from dblp_crawler import Graph, DBLPPerson, Publication

logger = logging.getLogger("graph")


def add_publication(tx, publication, added_journals: set, selected=False):
    n4jset = "MERGE (p:Publication {title_hash:$title_hash}) "\
        "SET p.dblp_key=$key, p.title=$title, p.year=$year"
    if publication.doi():
        n4jset += ", p.doi=$doi"
    if selected:
        n4jset += ", p.selected=true"
    tx.run(n4jset,
           title_hash=publication.title_hash(),
           key=publication.key(),
           title=publication.title(),
           year=publication.year(),
           doi=publication.doi())
    if publication.journal_key() and publication.journal_key() != "db/journals/corr":
        if publication.journal_key() not in added_journals:
            tx.run("MERGE (p:Journal {dblp_key:$dblp_key}) SET p.dblp_name=$dblp_name, p.ccf=$ccf",
                   dblp_key=publication.journal_key(),
                   dblp_name=publication.journal(),
                   ccf=publication.ccf())
            added_journals.add(publication.journal_key())
        tx.run("MERGE (p:Publication {title_hash:$title_hash})"
               "MERGE (j:Journal {dblp_key:$dblp_key})"
               "MERGE (p)-[:PUBLISH]->(j)",
               title_hash=publication.title_hash(),
               dblp_key=publication.journal_key())


def find_orcid(person):
    for publication in person.publications():
        for author in publication.authors():
            if author.pid() == person.pid():
                if author.orcid():
                    return author.orcid()


def add_person(tx, person: DBLPPerson, added_pubs: set, added_journals: set):
    orcid = find_orcid(person)
    n4jset = "MERGE (a:Person {dblp_pid: $pid}) "\
        "SET a.name=$name, a.affiliations=$aff"
    if orcid:
        n4jset += ", a.orcid=$orcid"
    tx.run(n4jset,
           pid=person.pid(), name=person.name(),
           aff=list(person.person().affiliations()),
           orcid=orcid)
    for publication in person.publications():
        tx.run("MERGE (a:Person {dblp_pid: $pid}) "
               "MERGE (p:Publication {title_hash: $title_hash}) "
               "MERGE (a)-[:WRITE]->(p)",
               pid=person.pid(),
               title_hash=publication.title_hash())
        if publication.key() not in added_pubs:
            add_publication(tx, publication, added_journals)
            added_pubs.add(publication.key())


def add_edge(tx, author_id, publication: Publication):
    tx.run("MERGE (a:Person {dblp_pid: $a}) "
           "MERGE (p:Publication {title_hash: $title_hash}) "
           "MERGE (a)-[:WRITE]->(p)",
           a=author_id,
           title_hash=publication.title_hash())


class Neo4jGraph(Graph, metaclass=abc.ABCMeta):
    def __init__(self, session: Session, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session = session
        self.added_pubs = set()
        self.added_journals = set()
        self.added_orcids = {}

    def summarize_person(self, a: str, person: Optional[DBLPPerson]):  # 构建summary
        if person is not None:
            self.session.execute_write(add_person, person, self.added_pubs, self.added_journals)  # 把作者信息加进图里

    def summarize_publication(self, authors_id, publication: Publication):  # 构建summary
        self.session.execute_write(add_publication, publication, self.added_journals, True)  # 把文章信息加进图里
        for a in authors_id:
            self.session.execute_write(add_edge, a, publication)  # 把边加进图里
        self.added_pubs.add(publication.key())
