#!/usr/bin/env python3

import sys
import urllib.request
import argparse
from pathlib import Path

ALLENNLP_MODELS = "https://s3-us-west-2.amazonaws.com/allennlp/models/"
DEPENDENCY = "biaffine-dependency-parser-ptb-2018.08.23.tar.gz"


def download(model, save_to=None):
    urllib.request.urlretrieve(ALLENNLP_MODELS + model, "data/allennlp/models/" + model)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Download ALLENNLP MODEL")

    parser.add_argument("--model", type=str,
                        help="Model", required=True)

    args = parser.parse_args(sys.argv[1:])
    download(args.model)
