from enum import Enum, auto

import pandas as pd
from radiology.params import ORIGINAL_BN, HYBRID_BN


def original_bn_diseases_names(original_bn: str = ORIGINAL_BN):
    with open(original_bn) as f:
        return list(pd.read_csv(f)["Disease"])


if __name__ == "__main__":
    print(original_bn_diseases_names())
    # with open(r"C:\Users\dhruv\git\radiology-nlp\data\unlabeled_neuro_reports\diseases.csv", "r") as f:
    #     kf = pd.read_csv(f)

    # # set(list(kf["ddx1"]) + list(kf["ddx2"]) + list(kf["ddx3"])):
    # for d in set(kf["ergo_name"]):
    #     print(d.upper() + " = auto()")
