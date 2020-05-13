# LSTM for sequence classification in the IMDB dataset
import numpy
import tensorflow as tf
# from tensorflow.keras.layers import Dense
# from keras.layers import LSTM
# from keras.layers import Embedding
# from keras.models import Sequential
# from keras.preprocessing import sequence
# from keras.preprocessing.text import Tokenizer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MultiLabelBinarizer

def unlabeled_reports_data(shuffle=False):
    filenames = os.listdir(params.UNLABELED_REPORTS_PATH)

    if shuffle:
        random.shuffle(filenames)

    dtm = disease_term_matching()

    for filename in os.listdir(params.UNLABELED_REPORTS_PATH):
        if filename.endswith(".csv"):
            disease = match_disease_label(
                filename.split(".csv")[0], dtm.values())
            with open(params.UNLABELED_REPORTS_PATH + filename, "r") as f:
                df = pd.read_csv(f)

            reports = list(zip(df["ID"], df["ReportText"]))
            if shuffle:
                random.shuffle(reports)

            for id, report in zip(df["ID"], df["ReportText"]):
                yield Report(id, DellHeaders.from_raw(report), report), disease


def unlabeled_prediction_dataset():
    ids = []
    findings = []
    labels = []

    for report, disease in unlabeled_reports_data():
        if len(report.get(DellHeaders.FINDINGS)) > 10:
            findings.append(report.get(DellHeaders.FINDINGS))
            labels.append(disease[0])
            ids.append(report.id)

    return ids, findings, labels


# fix random seed for reproducibility
numpy.random.seed(7)
# load the dataset but only keep the top n words, zero the rest
top_words = 5000

ids, reports, labels = unlabeled_prediction_dataset()


# reports = [r.body for i, r in enumerate(reports) if labels[i] in ["single", "multiple"]]
# labels = [d[l] for i, l in enumerate(labels) if labels[i] in ["single", "multiple"]]

mlb = MultiLabelBinarizer(sparse_output=False)
mlb.fit(labels)
labels = mlb.transform(labels)

tokenizer = tf.keras.preprocessing.text.Tokenizer(
    oov_token="<unk>", top_words=top_words)
tokenizer.fit_on_texts(reports)

report_seqs = tokenizer.texts_to_sequences(reports)

X_train, X_test, y_train, y_test = train_test_split(
    report_seqs, labels, test_size=0.2)


# truncate and pad input sequences
max_review_length = len(max(report_seqs, key=len))

X_train = tf.keras.preprocessing.sequence.pad_sequences(
    X_train, maxlen=max_review_length)
X_test = tf.keras.preprocessing.sequence.pad_sequences(
    X_test, maxlen=max_review_length)

# create the model
embedding_vecor_length = 300
model = tf.keras.layers.Sequential()
model.add(tf.keras.layers.Embedding(
    top_words, embedding_vecor_length, input_length=max_review_length))
model.add(tf.keras.layers.LSTM(100))
model.add(tf.keras.layers.Dense(1, activation='sigmoid'))
model.compile(loss='sparse_categorical_crossentropy',
              optimizer="adam", metrics=['accuracy'])
print(model.summary())
model.fit(X_train, y_train, epochs=10, batch_size=64)
# Final evaluation of the model
scores = model.evaluate(X_test, y_test, verbose=0)
print("Accuracy: %.2f%%" % (scores[1]*100))
