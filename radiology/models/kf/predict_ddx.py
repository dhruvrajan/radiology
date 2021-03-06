from radiology.datatypes.kf_labels import LabeledReports
from radiology.datatypes.reports import DellHeaders as DH
from radiology.params import NONE

from sklearn.dummy import DummyClassifier
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, f1_score
from radiology.models.kf.ddx_data import get_findings_disease_data





def unlabeled_prediction_dataset():
    return get_findings_disease_data()


def get_pipeline(clf) -> Pipeline:
    return Pipeline([
        ("vectorizer", CountVectorizer(ngram_range=(1, 2))),
        # ("tfidf", TfidfTransformer()),
        ("clf", clf)
    ])


dummy_clfs = [
    # ("dummy: stratified", DummyClassifier(strategy="stratified")),
    # ("dummy: most_frequent", DummyClassifier(strategy="most_frequent")),
    # ("dummy: maximize_prior", DummyClassifier(strategy="prior")),
    # ("dummy: uniform dist", DummyClassifier(strategy="uniform"))
]

clfs = [
    # ("logistic regression", LogisticRegression(solver="lbfgs")),
    ("SGD", SGDClassifier()),
    # ("multinomial naive bayes", MultinomialNB())
]


def run_classification(clf, clf_name, field, filter_none=True):
    # ids, reports, labels = kf_prediction_dataset(
    # field, filter_none=filter_none)
    ids, report_text, labels = unlabeled_prediction_dataset()
    # report_text = [report.get(DH.FINDINGS) for report in reports]
    pipeline = get_pipeline(clf)

    X_train, X_test, y_train, y_test, ids_train, ids_test = train_test_split(
        report_text, labels, ids)

    pipeline.fit(X=X_train, y=y_train)

    y_pred = pipeline.predict(X_test)

    return {
        "field": field,
        "clf": clf_name,
        "metrics": {
            "accuracy": accuracy_score(y_test, y_pred),
        }
    }


def run_experiment(field):
    logs = []

    print("FIELD:", field)
    for name, dummy in dummy_clfs:
        logs.append(run_classification(dummy, name, field))
        print(" =>", logs[-1]["clf"])
        print("   ", "accuracy =", logs[-1]["metrics"]["accuracy"])

    for name, clf in clfs:
        logs.append(run_classification(clf, name, field))
        print(" =>", logs[-1]["clf"])
        print("   ", "accuracy =", logs[-1]["metrics"]["accuracy"])


if __name__ == "__main__":
    run_experiment("known_ddx")
