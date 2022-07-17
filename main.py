from dblp_crawler import *

keywords = [
    r"video.+delivery",
    r"video.+streaming",
    r"video.+caching",
    r"video.+quality",
    r"super.+resolution",
    r"dash",
    r"360.+video",
    r"video.+360",
    r"vr.+video",
    r"video.+vr",
    r"video.+quality",
]


class GG(Graph):
    def filter_publications(self, publications):
        publications = filter_publications_by_keywords(publications, keywords)
        publications = filter_publications_after(publications, 2020)
        return publications


async def main():
    g = GG('74/1552-1')
    for i in range(5):
        await g.bfs_once()
    draw(g.networkx())


if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.INFO)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
