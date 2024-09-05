#!/usr/bin/env python
# coding: utf-8

from setuptools import setup

with open("README.md", "r", encoding='utf8') as fh:
    long_description = fh.read()

package_dir = {
    'dblp_crawler': 'dblp_crawler',
    'dblp_crawler.filter': 'dblp_crawler/filter',
    'dblp_crawler.data': 'dblp_crawler/data',
    'dblp_crawler.data.ccf': 'dblp_crawler/data/ccf',
    'dblp_crawler.keyword': 'dblp_crawler/keyword',
    'dblp_crawler.summarizer': 'dblp_crawler/summarizer',
}

setup(
    name='dblp_crawler',
    version='2.1.8',
    author='yindaheng98',
    author_email='yindaheng98@gmail.com',
    url='https://github.com/yindaheng98/dblp-crawler',
    description=u'异步高并发dblp爬虫，慎用',
    long_description=long_description,
    long_description_content_type="text/markdown",
    package_dir=package_dir,
    packages=[key for key in package_dir],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'networkx==2.*',
        'aiofile>=3.8.1',
        'aiohttp>=3.8.1',
        'neo4j>=5.5.0',
        'tqdm>=4.66.1',
    ],
)
