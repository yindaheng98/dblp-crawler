# dblp-crawler

Asynchronous high-concurrency dblp crawler, use with caution!

异步高并发dblp爬虫，慎用！

## Install

```sh
pip install dblp-crawler
```

## Usage

### Help

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
  -h, --help   show this help message and exit
  --auth AUTH  Auth to neo4j database.
  --uri URI    URI to neo4j database.
```

### Write to a JSON file

e.g. write to `summary.json`:

```sh
python -m dblp_crawler -k video -k edge -p l/JiangchuanLiu networkx --dest summary.json
```

### Write to a Neo4J database

e.g. write to `neo4j://10.128.202.18:7687`:

```sh
python -m dblp_crawler -k video -k edge -p l/JiangchuanLiu neo4j --uri neo4j://10.128.202.18:7687
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

e.g. init authors from ACM MM (`db/conf/mm` is the key for ACM MM in dblp: "https://dblp.org/db/conf/mm/index.xml")

```sh
python -m dblp_crawler -k video -k edge -j db/conf/mm networkx --dest summary.json
```