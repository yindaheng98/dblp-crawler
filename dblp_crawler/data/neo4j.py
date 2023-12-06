from neo4j import GraphDatabase


def match_authors(tx):
    authors = []
    for record in tx.run("MATCH (a:Person) RETURN a.dblp_pid"):
        for value in record.values():
            if value is not None:
                authors.append(value)
    return authors


def authors_in_neo4j(uri, auth=None):
    with GraphDatabase.driver(uri, auth=auth) as driver:
        with driver.session() as session:
            return session.execute_read(match_authors)
