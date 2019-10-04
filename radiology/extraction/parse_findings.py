import itertools
import time
from collections import defaultdict
from typing import DefaultDict, List

import torch
from allennlp.data.token_indexers.token_indexer import TokenIndexer
from allennlp.predictors.predictor import Predictor
from nltk import sent_tokenize

from radiology.loaders import Reports, labeled_reports
from radiology.types.reports import DellHeaders, Report

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

        # print(subj, root["children"])


def decompose_report(report):
    for sentence in sent_tokenize(report.get(DellHeaders.FINDINGS)):
        findings_from_sentence(sentence)

def locations(reports: List[Report]):
    mappings: DefaultDict = defaultdict(set)
    noun_map: DefaultDict = defaultdict(set)
    prep_map: DefaultDict = defaultdict(set)

    for i, report in enumerate(reports):
        print(i, report.id)
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

    for key, ns in mappings.items():
        print(">>>" + key)
        for n in ns:
            print(
                n + ";" + ";".join(list(noun_map[n])) + ";" + ";".join(list(map(str, prep_map[n]))))


if __name__ == "__main__":
    # print(parser.predict("There is a traveler with a stick."))
    # exit()
    reports = Reports.from_generator(labeled_reports)
    decompose_report(reports.get("1190577"))
    # print(reports.get("1190577").get(DellHeaders.FINDINGS))
    # locations([reports.get("1190577")])
    # N = 10
    # locations(list(itertools.islice(
    # filter(lambda r: r.get(DellHeaders.FINDINGS) != "", labeled_reports()), N)))
