from radiology.datatypes.diseases import hybrid_bn_diseases
from radiology.datatypes.reports import DellHeaders as DH
from radiology.loaders import Reports, unlabeled_reports
from nltk import sent_tokenize, word_tokenize
import re


def match_disease(text):
    diseases = hybrid_bn_diseases(use_ergo=False)
    diseases = set(
        [disease.split("(")[0].split(",")[0].strip().lower() for disease in diseases])

    disease_list = []
    for sent in sent_tokenize(text):
        for word in word_tokenize(sent):
            if word.lower() == "no":
                break
            elif word.lower() in diseases:
                disease_list += [word.lower()]

    return disease_list


if __name__ == "__main__":
    rs = Reports.from_generator(unlabeled_reports)

    for rid in rs.reports:
        findings = rs.reports[rid].get(DH.FINDINGS)
        impression = rs.reports[rid].get(DH.IMPRESSION)

        if len(findings) > 10 and len(impression) > 10:
            if re.match("[123456789]\.\s.*", impression):
                disease = match_disease(impression)
                if len(disease) > 0:
                    with open("examples/" + rid + ".txt", "w") as f:
                        f.write("Diseases: " + str(disease) + "\n")

                        f.write("FINDINGS:\n\n")
                        f.write(findings + "\n")

                        f.write("IMPRESSION:\n\n")
                        f.write(impression)
