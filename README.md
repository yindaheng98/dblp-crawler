# dblp-crawler

Asynchronous high-concurrency dblp crawler, use with caution!

异步高并发dblp爬虫，慎用！

Crawl papers from dblp and connect them into an undirected graph. Each edge is a paper, each node is an author.

从dblp爬文章并将其组织为无向图。图的边是文章，节点是作者。

Neo4J output compatible with [citation-crawler](https://github.com/yindaheng98/citation-crawler)

Neo4J形式的输出和[citation-crawler](https://github.com/yindaheng98/citation-crawler)兼容

![](asserts/graph.png)

## Install

```sh
pip install dblp-crawler
```

## Usage

```sh
python -m dblp_crawler -h
usage: __main__.py [-h] [-y YEAR] -k KEYWORD [-p PID] [-j JOURNAL] {networkx,neo4j} ...

positional arguments:
  {networkx,neo4j}      sub-command help
    networkx            networkx help
    neo4j               neo4j help

optional arguments:
  -h, --help            show this help message and exit
  -y YEAR, --year YEAR  Only crawl the paper after the specified year.
  -k KEYWORD, --keyword KEYWORD
                        Specify keyword rules.
  -p PID, --pid PID     Specified author pids to start crawling.
  -j JOURNAL, --journal JOURNAL
                        Specify author journal keys to start crawling.
```

```sh
python -m dblp_crawler networkx -h
usage: __main__.py networkx [-h] --dest DEST

optional arguments:
  -h, --help   show this help message and exit
  --dest DEST  Path to write results.
```

```sh
python -m dblp_crawler neo4j -h   
usage: __main__.py neo4j [-h] [--auth AUTH] --uri URI

optional arguments:
  -h, --help           show this help message and exit
  --username USERNAME  Auth username to neo4j database.
  --password PASSWORD  Auth password to neo4j database.
  --uri URI            URI to neo4j database.
  --select             Mark keyword-matched publications in database (set selected=true).
```

### Config environment variables

* `DBLP_CRAWLER_MAX_CACHE_DAYS_PERSON`: 
  * save cache for a person page for how many days
  * default: `30`
* `DBLP_CRAWLER_MAX_CACHE_DAYS_JOURNAL`: 
  * save cache for a journal page (e.g. [IEEE Transactions on Multimedia Volume 25, 2023](https://dblp.org/db/journals/tmm/tmm25.xml)) or conference page (e.g. [31st ACM Multimedia 2023](https://dblp.org/db/conf/mm/mm2023.xml)) for how many days
  * default: `-1` (cache forever)
* `DBLP_CRAWLER_MAX_CACHE_DAYS_JOURNAL_LIST`
  * save cache for a journal list page (e.g. [IEEE Transactions on Multimedia](https://dblp.org/db/journals/tmm/index.xml)) or conference list page (e.g. [ACM Multimedia](https://dblp.org/db/conf/mm/index.xml)) for how many days
  * default: `30`
* `HTTP_PROXY`
  * Set it `http://your_user:your_password@your_proxy_url:your_proxy_port` if you want to use proxy
* `HTTP_TIMEOUT`
  * Timeout for each http request, in seconds
* `HTTP_CONCORRENT`
  * Concurrent HTTP requests
  * default: `8`

### Write to a JSON file

e.g. write to `summary.json`:

```sh
python -m dblp_crawler -k video -k edge -p l/JiangchuanLiu networkx --dest summary.json
```

#### JSON format

```json
{
  "nodes": { // each node is a person
    "<dblp id of a person>": {
      "id": "<dblp id of this person>",
      "label": "<name in dblp>",
      "publications": [ // selected papers of this person (selected by "-k" and "-y" args)
        "<dblp id of a paper>",
        "<dblp id of a paper>",
        "<dblp id of a paper>",
        "......"
      ],
      "person": { // detailed data of this person
        "dblp_pid": "<dblp id of this person>",
        "name": "<name in dblp>",
        "affiliations": [
          "<affiliation of this person>",
          "<affiliation of this person>",
          "......"
        ],
        "publications": [ // all papers of this person
        "<dblp id of a paper>",
        "<dblp id of a paper>",
        "<dblp id of a paper>",
        "......"
        ]
      }
    },
    "<dblp id of a person>": { ...... },
    "<dblp id of a person>": { ...... },
    "<dblp id of a person>": { ...... },
    ......
  },
  "edges": { // each node is a cooperation of two person
    "<id of this edge>": {
      "from": "<dblp id of this person 1>",
      "to": "<dblp id of this person 2>",
      "publications": [ // selected papers that contain both this two persons as authors (selected by "-k" and "-y" args)
        "<dblp id of a paper>",
        "<dblp id of a paper>",
        "<dblp id of a paper>",
        "......"
      ],
      "cooperation": [ // all papers that contain both this two persons as authors (selected by "-k" and "-y" args)
        "<dblp id of a paper>",
        "<dblp id of a paper>",
        "<dblp id of a paper>",
        "......"
      ]
    },
    "publications": { // related publications
      "<dblp id of a paper>": {
      "key": "<dblp id of this paper>",
      "title": "<title of this paper>",
      "journal": "<name of the journal that this paper published on>",
      "journal_key": "<dblp id of the journal that this paper published on>",
      "year": "int <publish year of this paper>",
      "doi": "<doi of this paper>",
      "ccf": "A|B|C|N <CCF rank of this paper>",
      "authors": {
        "<dblp id of a person>": {
          "name": "<name in dblp>",
          "orcid": "<orcid of this person>"
        },
        "<dblp id of a person>": { ...... },
        "<dblp id of a person>": { ...... },
        ......
      },
      "selected": "true|false <whether the publication is selected (selected by -k and -y args)>"
      }
    }
  }
}
```

### Write to a Neo4J database

```sh
docker pull neo4j
docker run --rm -it --name neo4j -p 7474:7474 -p 7687:7687 -v "$(pwd)/save/neo4j:/data" -e NEO4J_AUTH=none neo4j
```

e.g. write to `neo4j://localhost:7687`:

```sh
python -m dblp_crawler -k video -k edge -p l/JiangchuanLiu neo4j --uri neo4j://localhost:7687
```

#### Tips

Without index, NEO4J query will be very very slow. So before you start, you should add some index:

```cql
CREATE INDEX publication_title_hash_index FOR (p:Publication) ON (p.title_hash);
CREATE INDEX publication_dblp_key_index FOR (p:Publication) ON (p.dblp_key);
CREATE INDEX publication_doi_index FOR (p:Publication) ON (p.doi);
CREATE INDEX person_dblp_pid_index FOR (p:Person) ON (p.dblp_pid);
CREATE INDEX journal_dblp_key_index FOR (p:Journal) ON (p.dblp_key);
```

### Only crawl the paper after specified year

e.g. crawl the paper after 2016 (include 2016)

```sh
python -m dblp_crawler -k video -k edge -p l/JiangchuanLiu -y 2016 networkx --dest summary.json
```

### Keywords with two or more words

e.g. super resolution (publications with title contains both "super" and "resolution" will be selected)

```sh
python -m dblp_crawler -k video -k edge -p l/JiangchuanLiu -k "'super','resolution'" networkx --dest summary.json
```

### Init authors from journal

e.g. init authors from ACM MM and MMSys (`db/conf/mm` is the key for ACM MM in dblp: "https://dblp.org/db/conf/mm/index.xml", `db/conf/mmsys` is the key for MMSys in dblp: "https://dblp.org/db/conf/mmsys/index.xml")

```sh
python -m dblp_crawler -k video -k edge -j db/conf/mm -j db/conf/mmsys networkx --dest summary.json
```

### Init authors from journal in some variables

e.g. there is a `CCF_A` in `dblp_crawler.data` contains keys of CCF A conferences, and MMSys is also great but not in CCF A

```sh
python -m dblp_crawler -k video -k edge -j "importlib.import_module('dblp_crawler.data').CCF_A" -j db/conf/mmsys networkx --dest summary.json
```

`importlib.import_module` is flexible, you can import your own variables through this.

### Init authors in some variables

e.g. want to crawl publications of those authors stored in neo4j database

```sh
python -m dblp_crawler -k video -k edge -p "importlib.import_module('dblp_crawler.data').authors_in_neo4j('neo4j://localhost:7687')" networkx --dest summary.json
```

`importlib.import_module` is flexible, you can import your own variables through this.

## `dblp_crawler.filter` Usage

Crawling papers takes a long time, so do not filter the papers in the crawling process. Instead, use a separate program `dblp_crawler`.filter` to filter the papers.

```sh
python -m dblp_crawler.filter -h                                                       
usage: __main__.py [-h] -i INPUT -o OUTPUT -f FILTER

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Input file path.
  -o OUTPUT, --output OUTPUT
                        Output file path.
  -f FILTER, --filter FILTER
                        Filter functions.
```

### Use internal filter

e.g. `drop_old_publications` is an internal function that drop publication by year

```sh
python -m dblp_crawler.filter -i summary.json -o summary.filter.json -f "lambda summary: drop_old_publications(summary, 2016)"
```

### Use multiple filters

e.g. `drop_old_publications` is an internal function that drop publications by year; `drop_nodes_by_all_publications` is an internal function that drop nodes by the sum of publications

```sh
python -m dblp_crawler.filter -i summary.json -o summary.filter.json \
  -f "lambda summary: drop_old_person_publications(summary, 2018)" \
  -f "lambda summary: drop_old_cooperation(summary, 2018)" \
  -f "lambda summary: drop_nodes_by_all_publications(summary, 4)" \
  -f "lambda summary: drop_edges_by_all_publications(summary, 4)"
```

### Use your own filter

e.g. another method to use `-f "lambda summary: drop_old_publications(summary, 2016)"`

```sh
python -m dblp_crawler.filter -i summary.json -o summary.filter.json -f "lambda summary: importlib.import_module('dblp_crawler.filter').drop_old_publications(summary, 2016)"
```

`importlib.import_module` is flexible, you can import your own variables through this.
