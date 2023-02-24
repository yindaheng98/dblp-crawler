import argparse
import logging
import json
import importlib
from dblp_crawler.filter import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('dblp_crawler.filter')

parser = argparse.ArgumentParser()

parser.add_argument("-i", "--input", type=str, required=True, help=f'Input file path.')
parser.add_argument("-o", "--output", type=str, required=True, help=f'Output file path.')
parser.add_argument("-f", "--filter", action='append', required=True, help=f'Filter functions.')
args = parser.parse_args()
with open(args.input) as source:
    summary = json.load(source)
    for fs in args.filter:
        logger.info("Applying: %s" % fs)
        summary = eval(fs)(summary)
    with open(args.output, 'w', encoding='utf8') as destin:
        json.dump(summary, destin, indent=2)
