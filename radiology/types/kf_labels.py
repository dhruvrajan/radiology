import pandas as pd
from radiology.params import KF_LABELS_PATH


def read_raw_kf_labels(kf_path: str = KF_LABELS_PATH):
    with open(kf_path) as f:
        return pd.read_csv(f)

def read_cleaned_kf_labels(kf_path: str = KF_LABELS_PATH):
    

if __name__ == "__main__":
    print(read_kf_labels())