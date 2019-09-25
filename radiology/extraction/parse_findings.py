from allennlp.predictors.predictor import Predictor
from allennlp.data.token_indexers.token_indexer import TokenIndexer
from collections import defaultdict
from typing import DefaultDict
from nltk import sent_tokenize
from radiology.loaders import labeled_reports
import itertools
import torch
import time

parser = Predictor.from_path(
    "data/models/biaffine-dependency-parser-ptb-2018.08.23.tar.gz", cuda_device=0)


def locations(reports):
    # t = time.time()
    # for i, r in enumerate(reports):
    #     for sentenece in sent_tokenize(r.findings):
    #         parser.predict(sentence=sentenece)

    # print("parsed in " + str(time.time() - t) + "seconds")

    # exit()
    mappings: DefaultDict = defaultdict(set)
    noun_map: DefaultDict = defaultdict(set)
    prep_map: DefaultDict = defaultdict(set)

    for i, report in enumerate(reports):
        print(i, report.id)
        for sentence in sent_tokenize(report.findings):
            tree = parser.predict(sentence=sentence)["hierplane_tree"]

            root = tree["root"]
            children = root["children"]

            if root["word"] in ["is", "are"]:
                nouns = list(map(lambda c: c["word"], filter(
                    lambda c: c["nodeType"] == "nsubj", children)))

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
    N = 5
    locations(list(itertools.islice(
        filter(lambda r: r.findings != "", labeled_reports()), N)))
