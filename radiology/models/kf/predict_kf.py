import abc
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

from radiology.datatypes.indexer import Indexer
from radiology.datatypes.kf_labels import LabeledReports
from radiology.datatypes.reports import DellHeaders as DH
from radiology.datatypes.diseases import hybrid_bn_diseases

diseases = hybrid_bn_diseases(use_ergo=False)


class KFClassifier:
    def __init__(self, desc=""):
        self.desc = desc

    @abc.abstractmethod
    def train(self, reports, labels, ids=None):
        pass

    @abc.abstractmethod
    def predict(self, reports):
        pass


class KFFeatureTransform:

    @abc.abstractmethod
    def fit(self, reports: [str]):
        pass

    @abc.abstractmethod
    def transform(self, reports: [str]):
        pass


class SklearnReportClassifier(KFClassifier):
    def __init__(self, clf, desc=""):
        super().__init__(desc)
        self.clf = clf

    def train(self, *args, **kwargs):
        return self.clf.fit(*args, **kwargs)

    def predict(self, *args, **kwargs):
        return self.clf.predict(*args, **kwargs)


class NGramFeatureExtractor(KFFeatureTransform):
    def __init__(self, ngram_range=(1, 3), stopwords=None):
        self.ngram_range = ngram_range
        self.stopwords = stopwords

        self.vectorizer = None
        self.feat_indexer = None

        self._initialize()

    def _initialize(self):
        self.vectorizer = CountVectorizer(
            ngram_range=self.ngram_range, stop_words=self.stopwords)
        self.feat_indexer = Indexer()

    def fit(self, reports):
        self.vectorizer.fit(reports)

    def transform(self, reports):
        X = self.vectorizer.transform(reports)

        for feat in self.vectorizer.get_feature_names():
            self.feat_indexer.get_index(feat, add=True)

        return X.toarray()


class ClassifierFromFeatureExtractor(KFClassifier):
    def __init__(self, clf: KFClassifier, feature_extractor: KFFeatureTransform):
        super().__init__()
        self.clf = clf
        self.feature_extractor = feature_extractor

    def train(self, X, y, *args, **kwargs):
        transformed = self.feature_extractor.transform(X)
        self.clf.train(transformed, y, *args, **kwargs)

    def predict(self, X):

        transformed = self.feature_extractor.transform(X)
        return self.clf.predict(transformed)

    def predict_single(self, X):
        transformed = self.feature_extractor.transform([X])
        return self.clf.predict(transformed)[0]


class KFEvaluator:
    def __init__(self):
        self.lr = LabeledReports.create()

    def evaluate_one_task(self, field, classifier: KFClassifier, feature_transform: KFFeatureTransform, test_size=0.33):
        report_obj, labels = zip(*self.lr.single_field_dataset(field))
        reports, ids = zip(*[(report.get(DH.FINDINGS), report.id)
                             for report in report_obj])
        feature_transform.fit(reports)
        reports = feature_transform.transform(reports)

        X_train, X_test, y_train, y_test, ids_train, ids_test = \
            train_test_split(reports, labels, ids, test_size=test_size)

        classifier.train(X_train, y_train, ids_train)

        train_pred = classifier.predict(X_train)
        test_pred = classifier.predict(X_test)
        summary = {
            "train_accuracy": accuracy_score(train_pred, y_train),
            "val_accuracy": accuracy_score(test_pred, y_test)
        }

        print("Evaluating KF Classifier:", classifier.desc, "on", field)
        print("    -> train_accuracy:", summary["train_accuracy"])
        print("    -> val_accuracy  :", summary["val_accuracy"])
        return summary

    def evaluate_all_one_task(self, fields, classifier, feature_transform, test_size=0.2):
        for field in fields:
            self.evaluate_one_task(
                field, classifier, feature_transform, test_size)


if __name__ == '__main__':

    kfe = KFEvaluator()
    kfe.evaluate_all_one_task(["known_ddx"],
                              SklearnReportClassifier(LogisticRegression()),
                              NGramFeatureExtractor((1, 2)))
