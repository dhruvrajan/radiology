import string
from typing import List, Tuple

import pandas as pd
import regex
from fuzzywuzzy import process
from nltk import sent_tokenize

from radiology.params import (FUZZY_DISEASE_MATCH_THRESHOLD,
                              HYBRID_BN_DISEASES, ORIGINAL_BN, NONE)

"""
Get lists of disease names.
"""


def hybrid_bn_diseases(hybrid_bn: str = HYBRID_BN_DISEASES, use_ergo=False) -> List[str]:
    with open(hybrid_bn) as f:
        df = pd.read_csv(f)
        return list(df["name"] if not use_ergo else df["ergo_name"])


def original_bn_diseases(original_bn: str = ORIGINAL_BN) -> List[str]:
    with open(original_bn) as f:
        df = pd.read_csv(f)
        return list(filter(lambda d: type(d) == str and not d.startswith("NOT"), df["disease"]))


def kf_diseases(kf):
    return set(list(kf["ddx1"]) + list(kf["ddx2"]) + list(kf["ddx3"]) + list(kf["known_ddx"])) - set([NONE])


"""
Match disease names in a body of text.
"""


def match_disease_label(fuzzy_label: str, diseases: List[str]) -> Tuple[str, float]:
    return process.extractOne(fuzzy_label, diseases)


def match_diseases_in_impression(impression: str, diseases: List[str],
                                 threshold=FUZZY_DISEASE_MATCH_THRESHOLD) -> Tuple[str, float]:

    def transform(s):
        s = s.split("([\m\w\.]")[0]
        return "(" \
            + s.strip(string.punctuation + string.whitespace) \
            .replace("(", "\(") \
            .replace(")", "\)") \
            .replace(" ", "\s") + ")" \
            + "{e<=%i}" % (0.3 * len(s) if len(s) > 5 else 1) + "\w\."

    ds = []
    for d in diseases:
        ds.append(d.split(",")[0])

    dss = []
    for d in ds:
        dss.extend(d.split("("))

    for i in range(len(dss)):
        dss[i] = dss[i].strip(string.punctuation + string.whitespace)

    dss = sorted(dss)
    for ds in dss:
        print(ds)

    pattern = "(" + "|".join(map(transform, dss)) + ")"
    predictions: dict = {}
    for sentence in sent_tokenize(impression.replace(".", ". ")):
        matches = list(regex.findall(pattern, sentence, ignore_case=True))
        for match in matches:
            disease, confidence = process.extractOne(match[0], diseases)
            if match[0].lower() not in disease.lower().split(string.whitespace + string.punctuation):
                confidence *= 0.75

            print(match[0], disease)
            if disease == "":
                continue
            if disease not in predictions:
                predictions[disease] = confidence
            else:
                predictions[disease] = max(confidence, predictions[disease])

    return sorted(predictions.items(), key=lambda p: -p[1])


if __name__ == "__main__":
    from radiology.datatypes.reports import DellHeaders
    from radiology.loaders import Reports, labeled_reports
    impression = Reports.from_generator(
        labeled_reports).pick_random()  # get("5853161")
    print(impression.id)
    impression = impression.get(DellHeaders.IMPRESSION)
    # impression = "Left hippocampus with increased signal, diminished size and abnormal internal architecture compatible with mesial temporal sclerosis."
    print(impression)

    # query = regex.compile("((Hypoxic Ischemic encephalopathy){e<=15}|(doggone){e<2})")
    # print(regex.findall(query, "ischemi encephalpathydoggne"))
    # print(match_disease_label("ischemi encephalpathy", hybrid_bn_diseases()))
    # print(original_bn_diseases())
    # impression = """Multiple lobulated rim enhancing lesions in bilateral frontal lobes and left periventricular/occipital horn, with
# non-enhancing restricted diffusion center, most likely multiple organized abscesses. Although there is significant surrounding
# edema, the modest nature may be related to partially treated infection.The moderately high rCBV along peripheral margin,
# however, is not as supportive for abscess. Necrotic neoplasms such as multiple metastasis is included in the differential but
# felt to be less likely."""
    print(match_diseases_in_impression(impression, hybrid_bn_diseases()))
