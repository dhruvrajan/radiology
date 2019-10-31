
from collections import defaultdict
from typing import DefaultDict

from allennlp.predictors.predictor import Predictor
from nltk import sent_tokenize
from nltk.corpus import stopwords
from radiology.datatypes.indexer import Indexer

from radiology.datatypes.kf_labels import LabeledReports
from radiology.datatypes.reports import DellHeaders

stops = stopwords.words('english')
parser = Predictor.from_path(
    "data/allennlp/models/biaffine-dependency-parser-ptb-2018.08.23.tar.gz")


def expand(node, sofar=[]):
    sofar += node
    if "children" in node.keys():
        for child in node["children"]:
            sofar = expand(child, sofar)
    return sofar


def find_one(node, of):
    if node['word'] in of:
        return node
    elif "children" in node.keys():
        try:
            return find_one(node["children"], of)
        except:
            return None
    else:
        return None


def sentence_to_chunks(sentence: str):
    tree = parser.predict(sentence)["hierplane_tree"]
    mappings: DefaultDict = defaultdict(set)
    noun_map: DefaultDict = defaultdict(set)
    prep_map: DefaultDict = defaultdict(set)

    preps = ["in", "around", "near", "of", "at", "by", "with"]

    root = tree["root"]

    if root["word"] not in ["is", "are", "shows", "indicates", "demonstrates"]:
        findone = find_one(
            root, ["is", "are", "shows", "indicates", "demonstrates"])
        root = findone if findone else root

    children = root["children"]
    if root["word"] in ["is", "are", "shows", "indicates", "demonstrates"]:
        nouns = list(map(lambda c: c["word"], filter(
            lambda c: c["nodeType"] in ["nsubj", "expl"], children)))

        for n in nouns:
            if n.lower() not in stops:
                noun_map[n] = set()

        for child in children:
            if "children" in child.keys():
                for c in child["children"]:
                    if c["nodeType"] in ["amod", "det"]:
                        noun_map[child["word"]].add(c["word"])
                    elif c["nodeType"] == "prep" or c["word"].lower() in preps:
                        if "children" in c.keys():
                            for co in c["children"]:
                                if co["nodeType"] == "pobj":
                                    prep_map[child["word"]].add(
                                        (c["word"], co["word"]))
            if child["nodeType"] == "prep" or child["word"].lower() in preps:
                if "children" in child.keys():
                    for co in child["children"]:
                        if co["nodeType"] == "pobj":
                            prep_map[child["word"]].add(
                                (child["word"], co["word"]))

        mappings[root["word"]].update(nouns)

        return root['word'], noun_map, prep_map
    return None


def sentence_to_chunks2(sentence: str):
    tree = parser.predict(sentence)["hierplane_tree"]
    mappings: DefaultDict = defaultdict(set)
    noun_map: DefaultDict = defaultdict(set)
    prep_map: DefaultDict = defaultdict(set)

    preps = ["in", "around", "near", "of", "at", "by", "with"]

    root = tree["root"]

    expanded = expand(tree['root'])

    for node in expanded:
        children = node["children"]
        if node in ["is", "are", "shows", "indicates", "demonstrates", "suggests"]:
            nouns = list(map(lambda c: c["word"], filter(
                lambda c: c["nodeType"] in ["nsubj", "expl"], children)))

            for n in nouns:
                if n.lower() not in stops:
                    noun_map[n] = set()

            for child in children:
                if "children" in child.keys():
                    for c in child["children"]:
                        if c["nodeType"] in ["amod", "det"]:
                            noun_map[child["word"]].add(c["word"])
                        elif c["nodeType"] == "prep" or c["word"].lower() in preps:
                            if "children" in c.keys():
                                for co in c["children"]:
                                    if co["nodeType"] == "pobj":
                                        prep_map[child["word"]].add(
                                            (c["word"], co["word"]))
                if child["nodeType"] == "prep" or child["word"].lower() in preps:
                    if "children" in child.keys():
                        for co in child["children"]:
                            if co["nodeType"] == "pobj":
                                prep_map[child["word"]].add(
                                    (child["word"], co["word"]))

            mappings[root["word"]].update(nouns)

            return root['word'], noun_map, prep_map
        elif node["nodeType"] in ["nsubj", "expl"]:
            for c in child["children"]:
                if c["nodeType"] in ["amod", "det"]:
                    noun_map[child["word"]].add(c["word"])
                elif c["nodeType"] == "prep" or c["word"].lower() in preps:
                    if "children" in c.keys():
                        for co in c["children"]:
                            if co["nodeType"] == "pobj":
                                prep_map[child["word"]].add(
                                    (c["word"], co["word"]))
                    return root['word'], noun_map, prep_map

    return None


def index_chunks(report_bodies):
    root_index = Indexer()
    noun_indexer = Indexer()
    amod_indexer = Indexer()
    prep_indexer = Indexer()

    for body in report_bodies:
        for sentence in sent_tokenize(body):
            result = sentence_to_chunks(sentence)

            if result:
                root, noun_map, prep_map = result
                root_index.get_index(root)

                for noun in noun_map:
                    noun_indexer.get_index(noun)
                    for amod in noun_map[noun]:
                        amod_indexer.get_index(amod)

                for prep_phrase in prep_map:
                    prep_indexer.get_index(prep_phrase)

                print("root:" + root)
                for n in noun_map:
                    print("   " + n)
                    for a in noun_map[n]:
                        print("      " + a)

                for a in prep_map:
                    print("   " + a)

    return root_index, noun_indexer, amod_indexer, prep_indexer


if __name__ == "__main__":
    lr = LabeledReports.create()

    bodies = ["""Motion degraded study. 
    Status post right decompressive craniectomy with 
    mild herniation of brain parenchyma through the defect. 
    Stable right hemispheric 8mm extra-axial hematoma. 
    Multiple bilateral parenchymal hemorrhages with adjacent 
    vasogenic edema and cerebral sulci effacement. 
    The largest is in the right parietal lobe measuring 3.1 x 2 cm. 
    Most were seen on prior head CT. Multiple smaller 
    adjacent punctate hemorrhages best seen on susceptibility 
    imaging were not well appreciated on prior head CT but are 
    unlikely to be new. No midline shift. Minimal perimesencephalic
     cistern effacement. Also noted is extensive T2 prolongation 
     in the bilateral cerebral white matter worse fon the right 
     but also involving the body of the corpus callosum. 
     Some but not all of these changes can be explained by edema 
     surrounding the hemorrhages suggesting a leukoencephalopathy. 
     There is signal abnormality in the left occipital lobe
      involving gray matter with sulcal effacement but without
       significant DWI signal or enhancement. This area shows
        hypodensity on the CT of 10/3/11 but not on the prior
         studies of 9/29/11. Partial opacification of the right
          mastoid air cells. There is patency of the i
          ntracranial circulation including the bilateral distal 
          vertebral arteries basilar artery and its distal 
          branches the bilateral intracranial internal 
          carotid arteries and the A1 and M1 segments. 
          There is a suggestion of diffuse narrowing of the 
          intracranial arteries perhaps artifactual or perhaps
           related to increased intracranial pressure. 
           Please note MRA is less sensitive for those aneurysms 
           under 4 mm. There is patency of the bilateral vertebral 
           arteries from their origins off of the subclavian arteries
            to the vertebral basilar junction. 
            The bilateral common carotid cervical internal
             carotid and external carotid arteries are patent 
             with no measurable stenosis. Probable stenosis of the 
             left vertebral artery at the approximate C4 level 
             best seen on the gadolinium-enhanced MRA. 
             There is a focus of flow-related enhancement 
             adjacent to the left vertebral artery perhaps a 
             small aneurysm at the left PICA origin. 
"""]

    index_chunks(bodies)
