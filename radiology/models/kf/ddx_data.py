import os
import re
import pandas as pd
import random
from radiology.datatypes.reports import Report, DellHeaders
from radiology.datatypes.diseases import match_disease_label
from radiology import params
from typing import Iterator


def disease_term_matching(fr="UNLABELED", to="UNLABELED_ERGO") -> pd.DataFrame:
    with open(params.DISEASE_TERM_MATCHING) as f:
        df = pd.read_csv(f)

    return {f: t for (f, t) in zip(list(df[fr]), list(df[to]))}


def unlabeled_reports_data(shuffle=False):
    filenames = os.listdir(params.UNLABELED_REPORTS_PATH)

    if shuffle:
        random.shuffle(filenames)

    dtm = disease_term_matching()

    for filename in os.listdir(params.UNLABELED_REPORTS_PATH):
        if filename.endswith(".csv"):
            disease = match_disease_label(
                filename.split(".csv")[0], dtm.values())
            with open(params.UNLABELED_REPORTS_PATH + filename, "r") as f:
                df = pd.read_csv(f)

            reports = list(zip(df["ID"], df["ReportText"]))
            if shuffle:
                random.shuffle(reports)

            for id, report in zip(df["ID"], df["ReportText"]):
                yield Report(id, DellHeaders.from_raw(report), report), disease


def get_findings_disease_data():
    ids = []
    findings = []
    labels = []

    for report, disease in unlabeled_reports_data():
        if len(report.get(DellHeaders.FINDINGS)) > 10:
            findings.append(report.get(DellHeaders.FINDINGS))
            labels.append(disease[0])
            ids.append(report.id)

    return ids, findings, labels


if __name__ == "__main__":
    list(unlabeled_reports_data())
