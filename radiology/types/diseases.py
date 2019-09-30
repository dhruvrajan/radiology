import pandas as pd
from typing import Tuple, List
from radiology.params import HYBRID_BN_DISEASES
from fuzzywuzzy import process


"""
Using Hybrid BN as index for diseases
"""


def diseases(hybrid_bn_diseases: str = HYBRID_BN_DISEASES):
    with open(hybrid_bn_diseases) as f:
        df = pd.read_csv(f)
        return dict(zip(df["ergo_name"], df["disease_id"]))


def match_disease(disease: str, among: List[str]) -> Tuple[str, float]:
    return process.extractOne(disease, among)

