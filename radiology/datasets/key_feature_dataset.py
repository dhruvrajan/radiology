from typing import List

from nltk import sent_tokenize, word_tokenize
from nltk.corpus import stopwords

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
from sklearn.feature_extraction.text import CountVectorizer
from radiology.datatypes.indexer import Indexer, indexer_from_values
from radiology.datatypes.kf_labels import LabeledReports
from radiology.datatypes.reports import DellHeaders
import numpy as np
from sklearn.linear_model import LogisticRegression

from radiology.loaders import Reports
from radiology.params import NONE, PAD_SYMBOL, UNK_SYMBOL, KF_EMISSIONS


def create_vocabulary(reports: List[str], use_stopwords=False) -> Indexer:
    stopwords_list = set()
    if use_stopwords:
        stopwords_list = set(stopwords.words("english"))

    indexer = Indexer()
    for report_text in reports:
        for sentence in sent_tokenize(report_text):
            for word in word_tokenize(sentence):
                if word not in stopwords_list:
                    indexer.get_index(word.strip().lower(), add=True)

    return indexer


def raw_text_kf_data(*fields, filter_none=False):
    lr = LabeledReports.create()
    ids, reports, labels = [], [], []

    for id in lr.reports.keys():
        consensus = [lr.consensus(id, field) for field in fields]
        if not (filter_none and NONE in consensus):
            ids.append(id)
            reports.append(lr.reports[id])
            labels.append(consensus if len(fields) > 1 else consensus[0])

    return ids, reports, labels


def index_labels():
    return {field: indexer_from_values(KF_EMISSIONS[field], in_order=True) for field in KF_EMISSIONS}


def indexed_kf_data(*fields, filter_none=False):
    ids, reports, labels = raw_text_kf_data(*fields, filter_none=filter_none)

    findings = map(lambda report: report.get(DellHeaders.FINDINGS), reports)
    examples = zip(findings, labels)
    examples = list(filter(lambda e: len(e[1]) > 0, examples))

    Xs, ys = zip(*examples)

    word_index = create_vocabulary(findings)
    label_index = index_labels()

    return word_index, label_index, ids, Xs, ys


def encode_one_hot(labels, integer=False):
    label_encoder = LabelEncoder()
    onehot_encoder = OneHotEncoder(sparse=False)

    integer_encoded = label_encoder.fit_transform(labels)
    integer_encoded = integer_encoded.reshape(len(integer_encoded), 1)

    if integer:
        return integer_encoded

    onehot_encoded = onehot_encoder.fit_transform(integer_encoded)

    return onehot_encoded


def word_count_vectors(reports, ngrams=(1, 2)):
    vectorizer = CountVectorizer(ngram_range=ngrams)
    return vectorizer.fit_transform(reports)


def kf_word_count_one_hot_dataset(field, test_split=0.3):
    word_index, label_index, ids, reports, labels = indexed_kf_data(
        field, filter_none=True)

    X = word_count_vectors(reports).todense()
    y = encode_one_hot(labels)

    return train_test_split(X, y, test_size=test_split)


def kf_word_count_integer_dataset(field, test_split=0.3):
    word_index, label_index, ids, reports, labels = indexed_kf_data(field, filter_none=True)

    X = word_count_vectors(reports).todense()
    y = encode_one_hot(labels, integer=True)

    return train_test_split(X, y, test_size=test_split)


if __name__ == "__main__":
    X_train, X_test, y_train, y_test = kf_word_count_one_hot_dataset(
        "mass_effect")

    clf = LogisticRegression()
    clf.fit(X_train, y_train)
