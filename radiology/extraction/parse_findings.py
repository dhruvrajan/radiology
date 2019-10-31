from collections import defaultdict
from typing import DefaultDict

from allennlp.predictors.predictor import Predictor
from nltk import sent_tokenize

from radiology.datatypes.reports import DellHeaders

parser = Predictor.from_path(
    "data/allennlp/models/biaffine-dependency-parser-ptb-2018.08.23.tar.gz")


def findings_from_sentence(sentence: str):
    print(sentence)
    tree = parser.predict(sentence)["hierplane_tree"]
    root = tree["root"]

    if root["word"] in ["is", "are", "shows"]:
        subj = [child["word"]
                for child in root["children"] if child["nodeType"] in ["nsubj", "expl", "shows", "amod"]]
        print(subj)

def decompose_report(report):
    for sentence in sent_tokenize(report.get(DellHeaders.FINDINGS)):
        findings_from_sentence(sentence)


def locations(reports, kf, f=None):
    disease_mappings: DefaultDict = defaultdict(set)
    mappings: DefaultDict = defaultdict(set)
    noun_map: DefaultDict = defaultdict(set)
    prep_map: DefaultDict = defaultdict(set)
    fnouns = set()
    for i, (id, report) in enumerate(reports.all_reports()):
        try:
           # print(i, id)
            for sentence in sent_tokenize(report.get(DellHeaders.FINDINGS)):
                tree = parser.predict(sentence=sentence)["hierplane_tree"]

                root = tree["root"]
                children = root["children"]

                if root["word"] in ["is", "are", "shows", "indicates", "demonstrates"]:
                    nouns = list(map(lambda c: c["word"], filter(
                        lambda c: c["nodeType"] in ["nsubj", "expl"], children)))

                    for n in children:
                        if "children" in n.keys():
                            for c in n["children"]:
                                if c["nodeType"] == "amod":
                                    noun_map[n["word"]].add(c["word"])
                                elif c["nodeType"] == "prep":
                                    if "children" in c.keys():
                                        for co in c["children"]:
                                            if co["nodeType"] == "pobj":
                                                prep_map[n["word"]].add(
                                                    (c["word"], co["word"]))

                    mappings[root["word"]].update(nouns)
                    for n in nouns:
                        fnouns.add(n)
            try:
                for sentence in sent_tokenize(report.get(DellHeaders.IMPRESSION)):
                    tree = parser.predict(sentence=sentence)["hierplane_tree"]

                    root = tree["root"]
                    children = root["children"]

                    if root["word"] in ["is", "are", "shows", "indicates", "demonstrates"]:
                        nouns = list(map(lambda c: c["word"], filter(
                            lambda c: c["nodeType"] in ["nsubj", "expl"], children)))

                        for n in children:
                            if "children" in n.keys():
                                for c in n["children"]:
                                    if c["nodeType"] == "amod":
                                        noun_map[n["word"]].add(c["word"])
                                    elif c["nodeType"] == "prep":
                                        if "children" in c.keys():
                                            for co in c["children"]:
                                                if co["nodeType"] == "pobj":
                                                    prep_map[n["word"]].add(
                                                        (c["word"], co["word"]))

                        mappings[root["word"]].update(nouns)
                        for n in nouns:
                            if n in fnouns:
                                print(n)
            except:
                pass
        except:
            pass
    for key, ns in mappings.items():
        f.write(">>>" + key + "\n")
        for n in ns:
            f.write(n + ";" + ";".join(list(noun_map[n])) +
                    ";" + ";".join(list(map(str, prep_map[n]))) + "\n")


if __name__ == "__main__":
    # print(parser.predict("There is a traveler with a stick."))
    # exit()
    #     reports = LabeledReports(list_labeled_reports(), read_raw_kf_labels())
    # )

    # decompose_report(reports.get("1190577"))
    # print(reports.get("1190577").get(DellHeaders.FINDINGS))
    # locations([reports.get("1190577")])
    # N = 300
    # with open("parse_findings_out2.csv", "w") as f:
    #     locations(LabeledReports(list(itertools.islice(
    #         filter(lambda r: r.get(DellHeaders.FINDINGS) != "", unlabeled_reports()), N)), read_raw_kf_labels()), f)