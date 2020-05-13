import pandas as pd
from collections import defaultdict
from radiology.params import HYBRID_BN_TABLE, HYBRID_BN_DISEASES


class HybridDiagnosisModel():
    """
    Hybrid Model:
       - P(D | F) = P(F | D) * P(D) / (P(D) * P (F | D) + P(-D) * P(F | -D))
    """

    def __init__(self):
        # Read disease ids
        with open(HYBRID_BN_DISEASES) as f:
            df = pd.read_csv(f)

        self.disease_table = df

        info = zip(list(df["disease_id"]),
                   list(df["ergo_name"]),
                   list(df["prevalence"]))

        diseases = {
            disease_id: {
                "ergo_name": ergo_name.lower(),
                "prevalence": prevalence
            } for disease_id, ergo_name, prevalence in info
        }

        # Read BN Model
        with open(HYBRID_BN_TABLE) as f:
            df = pd.read_csv(f)

        self.disease_map = diseases
        self.hybrid_model = df

    def list_fields(self):
        fields = defaultdict(set)
        for key in self.hybrid_model.keys()[2:]:
            field, emission, _ = key.split("/")
            fields[field].add(emission)

        return fields

    def disease(self, disease_id):
        return self.disease_table[self.disease_table["disease_id"] == disease_id]["prevalence"][0]

    def not_disease(self, disease_id):
        return 1 - self.disease(disease_id)

    def feature_given_disease(self, feature, emission, disease):
        label = "/".join([feature, emission, "yp"])
        return self.hybrid_model[self.hybrid_model["disease"] == disease][label][0]

    def feature_given_not_disease(self, feature, emission, disease):
        label = "/".join([feature, emission, "np"])
        return self.hybrid_model[self.hybrid_model["disease"] == disease][label][0]

    def disease_given_feature(self, feature, emission, disease):
        return self.feature_given_disease(feature, emission, disease) * self.disease(disease) \
               / (self.disease(disease) * self.feature_given_disease(feature, emission, disease)
                  + self.not_disease(disease) * self.feature_given_not_disease(feature, emission, disease))

    def disease_given_features(self, features, disease):
        return


if __name__ == "__main__":
    hm = HybridDiagnosisModel()
    print(hm.disease(1))
    print(hm.feature_given_disease("adc", "decreased", 1))
