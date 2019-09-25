import os
import random
import pandas as pd
import itertools
from typing import List, Iterator
import radiology.params as params
from radiology.types.reports import Report, DellHeaders


def labeled_reports(shuffle=False) -> Iterator[Report]:
    reports = list(filter(lambda filename:
                          filename.endswith(".txt"), os.listdir(params.LABELED_REPORTS_PATH)))

    if shuffle:
        random.shuffle(reports)

    for filename in reports:
        if filename.endswith(".txt"):
            with open(params.LABELED_REPORTS_PATH + filename, "r") as f:
                yield Report(filename.split(".")[0], DellHeaders.from_raw(f.read()))


def unlabeled_reports() -> Iterator[Report]:
    for filename in os.listdir(params.UNLABELED_REPORTS_PATH):
        if filename.endswith(".csv"):
            with open(params.UNLABELED_REPORTS_PATH + filename, "r") as f:
                df = pd.read_csv(f)

            for id, report in zip(df["ID"], df["ReportText"]):
                yield Report(id, DellHeaders.from_raw(report))


def all_reports() -> Iterator[Report]:
    yield from labeled_reports()
    yield from unlabeled_reports()


def list_labeled_reports(n=None, shuffle=False) -> List[Report]:
    return list(itertools.islice(labeled_reports(shuffle=shuffle), n))


def list_unlabeled_reports(n=None) -> List[Report]:
    return list(itertools.islice(unlabeled_reports(), n))


def list_all_reports(n=None) -> List[Report]:
    return list(itertools.islice(all_reports(), n))


if __name__ == "__main__":
    print(list_all_reports()[500].sections)
