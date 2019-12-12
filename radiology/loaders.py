import itertools
import os
import random
from typing import List, Iterator

import pandas as pd

import radiology.params as params
from radiology.datatypes.reports import Report, DellHeaders
from fuzzywuzzy import process


def labeled_reports(shuffle=False) -> Iterator[Report]:
    reports = list(filter(lambda filename: filename.endswith(".txt"), os.listdir(params.LABELED_REPORTS_PATH)))

    if shuffle:
        random.shuffle(reports)

    for filename in reports:
        if filename.endswith(".txt"):
            with open(params.LABELED_REPORTS_PATH + filename, "r") as f:
                raw = f.read()
                yield Report(filename.split(".")[0], DellHeaders.from_raw(raw), raw)


def unlabeled_reports(diseases=None, shuffle=False) -> Iterator[Report]:
    files = os.listdir(params.UNLABELED_REPORTS_PATH)
    if not diseases:
        filenames = files
    else:
        filenames = []
        for d in diseases:
            for fn in files:
                if d.lower() in fn.lower():
                    filenames.append(fn)

    if shuffle:
        random.shuffle(filenames)

    for filename in filenames:
        if filename.endswith(".csv"):
            with open(params.UNLABELED_REPORTS_PATH + filename, "r") as f:
                df = pd.read_csv(f)

            reports = list(zip(df["ID"], df["ReportText"]))
            if shuffle:
                random.shuffle(reports)

            for id, report in zip(df["ID"], df["ReportText"]):
                yield Report(id, DellHeaders.from_raw(report), report)


def all_reports() -> Iterator[Report]:
    yield from labeled_reports()
    yield from unlabeled_reports()


def list_labeled_reports(n=None, shuffle=False) -> List[Report]:
    return list(itertools.islice(labeled_reports(shuffle=shuffle), n))


def list_unlabeled_reports(n=None) -> List[Report]:
    return list(itertools.islice(unlabeled_reports(), n))


def list_all_reports(n=None) -> List[Report]:
    return list(itertools.islice(all_reports(), n))


class Reports:
    def __init__(self, reports: List[Report]):
        self.reports = {report.id: report for report in reports}

    def get(self, report_id: str):
        return self.reports[report_id]

    def pick_random(self):
        return self.get(random.choice(list(self.reports.keys())))

    @staticmethod
    def labeled(shuffle=False):
        return Reports.from_reports(labeled_reports(shuffle))

    @staticmethod
    def unlabeled(shuffle=False):
        return Reports.from_reports(unlabeled_reports(shuffle))

    @staticmethod
    def all(shuffle=False):
        return Reports.from_reports(all_reports(shuffle))

    @staticmethod
    def from_reports(reports):
        return Reports(reports)

    @staticmethod
    def from_generator(gen):
        return Reports(list(gen()))

