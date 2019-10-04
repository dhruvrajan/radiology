#!/usr/bin/env python3

import sys
import argparse
import subprocess
from pathlib import Path

DELL_DATA_URL = "https://github.com/dhruvrajan/dell_medical_data"
DEFAULT_SAVE_TO = "./data"


def download(save_to):
    subprocess.run("git clone %s %s" % (DELL_DATA_URL, save_to), shell=True, check=True)

    if save_to != DEFAULT_SAVE_TO:
        Path(DEFAULT_SAVE_TO).symlink_to(save_to)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Download Dell Radiology Report Data from %s" % DELL_DATA_URL)

    parser.add_argument("--save-to", type=str,
                        help="Path to save reports to.", default=DEFAULT_SAVE_TO)

    args = parser.parse_args(sys.argv[1:])
    download(args.save_to)
