"""python -m scripts.map_pipeline のエントリポイント"""
import argparse

from .cli import main

parser = argparse.ArgumentParser()
parser.add_argument("--max-papers", type=int, default=10000)
parser.add_argument("--log", action="store_true")
args = parser.parse_args()
main(args.max_papers, log=args.log)
