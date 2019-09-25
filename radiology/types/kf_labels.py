import pandas as pd
from radiology.params import KF_LABELS_PATH


def read_kf_labels(kf_path: str=KF_LABELS_PATH):
    with open(kf_path) as f:
        kf = pd.read_csv(f)

    