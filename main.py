from dblp_crawler import *

keywords = [
    "video",
    "streaming",
    "resolution"
]


class GG(Graph):
    def filter_publications(self, publications):
        publications = filter_publications_by_keywords(publications, keywords)
        publications = filter_publications_after(publications, 2020)
        return publications


async def main():
    g = GG('74/1552-1')
    for i in range(3):
        await g.bfs_once()
    draw(g.networkx())


if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.DEBUG)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
