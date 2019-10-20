import re
import string
from typing import List

import pandas as pd

from radiology import params
from radiology.datatypes.reports import Report
from radiology.loaders import Reports, list_labeled_reports
from radiology.params import KF_LABELS_PATH, ID_MAP_PATH, NONE
from radiology.utils import case


def read_raw_kf_labels(kf_path: str = KF_LABELS_PATH):
    with open(kf_path) as f:
        return pd.read_csv(f)


def get_id_map(path=ID_MAP_PATH):
    """
    Load accession id mapping from ocr output.
    :return: to and fr: dictionaries representing forward/backward id translation
    to: Accession # -> KF case_id
    fr: KF case_id -> Accession #
    """
    to = dict()
    fr = dict()

    for i in range(10):
        with open(path + "galileo_%i.txt" % i, "r", encoding="utf-16") as f:
            l1, l2 = map(int, f.readline().split(","))
            for line in f:
                idx1 = line[l1 - 1:].split(" ")[0].strip()
                idx2 = line[l2 - 1:].split(" ")[0].strip()

                to[idx1] = idx2
                fr[idx2] = idx1

    return to, fr


def transform_location_field(kf: pd.DataFrame):
    def matches(location, location_text):
        return location if location in " ".join(re.split("[\W;]", location_text.strip().lower())) else NONE

    kf["location_cerebral"] = kf["location"].map(
        lambda x: matches("cerebral", x))
    kf["location_cortical"] = kf["location"].map(
        lambda x: matches("cortical", x))
    kf["location_cerebellum"] = kf["location"].map(
        lambda x: matches("cerebellum", x))
    kf["location_deep_gray"] = kf["location"].map(
        lambda x: "deep_gray" if "deep gray" in x else NONE)
    kf["location_extracerebral"] = kf["location"].map(
        lambda x: matches("extracerebral", x))
    kf["location_intraventricular"] = kf["location"].map(
        lambda x: matches("intraventricular", x))
    kf["location_brain_stem"] = kf["location"].map(
        lambda x: "brain_stem" if "brain stem" in x else NONE)

    return kf


def split_disease(disease):
    disease = disease.lower()
    nicknames = re.findall(r"\(([^)]+)", disease)
    if len(nicknames) > 0:
        nicknames = [n.strip() for n in nicknames[0].split(",")]

    disease = "".join([c for c in (disease[:disease.find("(")]
                                   if "(" in disease else disease)
                       if c not in string.punctuation]).strip()

    result = "\"" + disease + \
        (" " + "<(" + ", ".join(nicknames) + ")>" if len(nicknames) > 0 else "") + "\""

    return disease, nicknames, result


def kf_ddx_to_bn_disease(ddx):
    return split_disease(ddx)[0].strip(string.whitespace)


def transform_ddx_fields(kf: pd.DataFrame):
    def ddx_transform(ddx):
        transformed = kf_ddx_to_bn_disease(ddx)
        return transformed
        # common = set(COMMON_DISEASES)
        # if transformed in common:
        #     return transformed
        # #print("UNCOMMON:", transformed)
        # return UNK_SYMBOL

    kf["ddx1"] = kf["ddx1"].map(ddx_transform)
    kf["ddx2"] = kf["ddx2"].map(ddx_transform)
    kf["ddx3"] = kf["ddx3"].map(ddx_transform)
    kf["known_ddx"] = kf["known_ddx"].map(ddx_transform)

    return kf


def read_kf_labels():
    kf = read_raw_kf_labels()
    kf = kf.fillna(NONE)
    kf = transform_ddx_fields(kf)
    kf = transform_location_field(kf)
    return kf


class LabeledReports(Reports):
    def __init__(self, reports: List[Report], kf: pd.DataFrame):
        super().__init__(reports)
        self.kf = kf

    def field(self, field, level=2):
        return [self.consensus(report.id, field, level) for report in self.reports]

    def consensus(self, id, field, level=2, to=get_id_map()[0]):
        assert level in [0, 1, 2]
        reader_threshold = case(level, {
            0: params.ATTENDING_THRESHOLD,
            1: params.FELLOW_THRESHOLD,
            2: max(set(self.kf["reader_id"])) + 1
        })

        annotations = self.kf[self.kf["case_id"] ==
                              to[id]][self.kf["reader_id"] < reader_threshold][field]
        try: 
            return max(list(set(annotations)), key=list(annotations).count)
        except ValueError:
            return None

    def single_field_dataset(self, field: str):
        to, _ = get_id_map()
        for report in self.reports.values():
            yield (report, self.consensus(report.id, field, to=to))

    @staticmethod
    def create():
        return LabeledReports(list_labeled_reports(), read_kf_labels())

if __name__ == '__main__':
    lr = LabeledReports.create()