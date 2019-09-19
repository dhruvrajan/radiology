import os
import pandas as pd
from typing import List, Iterator
import radiology_nlp.params as params
from radiology_nlp.types.reports import Report, raw_to_report


def labeled_reports() -> Iterator[Report]:
    for filename in os.listdir(params.LABELED_REPORTS_PATH):
        if filename.endswith(".txt"):
            with open(params.LABELED_REPORTS_PATH + filename, "r") as f:
                yield raw_to_report(filename.split(".")[0], f.read())


def unlabeled_reports() -> Iterator[Report]:
    for filename in os.listdir(params.UNLABELED_REPORTS_PATH):
        if filename.endswith(".csv"):
            with open(params.UNLABELED_REPORTS_PATH + filename, "r") as f:
                df = pd.read_csv(f)

            for id, report in zip(df["ID"], df["ReportText"]):
                yield raw_to_report(id, report)


def all_reports() -> Iterator[Report]:
    yield from labeled_reports()
    yield from unlabeled_reports()


def list_labeled_reports() -> List[Report]:
    return list(labeled_reports())


def list_unlabeled_reports() -> List[Report]:
    return list(unlabeled_reports())


def list_all_reports() -> List[Report]:
    return list(all_reports())


if __name__ == "__main__":
    print(len(list_all_reports()))