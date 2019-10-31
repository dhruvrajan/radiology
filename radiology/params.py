import pandas as pd

# Data File Paths
LABELED_REPORTS_PATH = "data/labeled_neuro_reports/reports/"
UNLABELED_REPORTS_PATH = "data/unlabeled_neuro_reports/reports/"
UNLABELED_DISEASES = "data/unlabeled_neuro_reports/diseases.csv"
KF_LABELS_PATH = "data/labeled_neuro_reports/kf_ground_truth_commas.csv"
ID_MAP_PATH = "data/labeled_neuro_reports/galileo_index/"


ORIGINAL_BN = "data/bayes_network/original/renamed_network.csv"
HYBRID_BN_TABLE = "data/bayes_network/hybrid/hybrid_bn.csv"
HYBRID_BN_DISEASES = "data/bayes_network/hybrid/diseases.csv"

DISEASE_TERM_MATCHING = "data/matching/disease_term_matching.csv"

# Symbols
NONE = "<NONE>"
PAD_SYMBOL = "<PAD>"
UNK_SYMBOL = "<UNK>"

# Reader IDs
ATTENDING_THRESHOLD = 21
FELLOW_THRESHOLD = 41

# Tunable Numbers
FUZZY_DISEASE_MATCH_THRESHOLD = 50

# Labeled KF Params (335)
KF_LOCATION_KEYS = ["location_cerebral",
                    "location_cortical",
                    "location_deep_gray",
                    "location_extracerebral",
                    "location_intraventricular",
                    "location_brain_stem"]

KF_EMISSIONS = {
    "t1": ["increased", "normal", "decreased"],
    "t2": ["increased", "normal", "decreased"],
    "flair": ["increased", "normal", "decreased"],
    "susceptibility_artifact": ["yes", "no"],
    "mass_effect": ["positive", "none", "negative"],
    "number_of_lesions": ["single", "multiple"],
    "size": ["small", "medium", "large"],
    "side": ["right", "left", "bilateral_symmetric", "bilateral_asymmetric"],
    "diffusion": ["facilitated", "normal", "restricted"],
    "location_cerebral": ["cerebral"],
    "location_cortical": ["cortical"],
    "location_cerebellum": ["cerebellum"],
    "location_deep_gray": ["deep_gray"],
    "location_extracerebral": ["extracerebral"],
    "location_intraventricular": ["intraventricular"],
    "location_brain_stem": ["brain_stem"],
    "contrast_enhancement": ["yes", "no"],
    "pattern": ['ring', 'heterogeneous', 'homogeneous']
}


# Valid DDX Labels
with open(DISEASE_TERM_MATCHING) as f:
    VALID_DISEASE_LABELS = set(pd.read_csv(f)["UNLABELED_ERGO"])
