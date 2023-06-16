"""
    Recursive feature elimination (RFE) with logistic regression as estimator
"""

from pydoc import doc
from utils_data_processing import preprocess_imdb
import os
from sklearn.model_selection import cross_val_score
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import MaxAbsScaler
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from utils_data_processing import LinearPipeline
from sklearn.feature_selection import RFE
import utils

ngram_range = (1, 2)
min_df = 2
C = 0.5
n_folds = 5
num_jobs = -1
ngram = 2
num_features = 10000
step = 10000


if __name__ == "__main__":
    traindata, _, testdata = preprocess_imdb(num_jobs=num_jobs)

    cache_name = "imdb_wrapper.pkz"
    try:
        X_train, y_train, X_test, y_test, vocabulary = utils.load_cache(
            cache_name, ["X_train", "y_train", "X_test", "y_test", "vocabulary"]
        )
    except RuntimeError as err:
        traindata, _, testdata = preprocess_imdb(num_jobs=num_jobs)


        print("Vectorizing the data")
        vectorizer = CountVectorizer(ngram_range=(1, ngram), min_df=2)
        X_train = vectorizer.fit_transform(traindata.data)
        y_train = traindata.target
        X_test = vectorizer.transform(testdata.data)
        y_test = testdata.target
        vocabulary = np.array(vectorizer.get_feature_names_out())

        utils.save_cache(
            cache_name,
            {
                "X_train": X_train,
                "y_train": y_train,
                "X_test": X_test,
                "y_test": y_test,
                "vocabulary": vocabulary,
            },
        )
    print(f"Original vocabulary size : {len(vocabulary)}")

    """
    Add lines here
    """
    pipeline = Pipeline(
        [
            ("scaler", MaxAbsScaler()),
            ("clf", LogisticRegression(C=C, solver="liblinear", random_state=42)),
        ]
    )

    classifier = LinearPipeline(pipeline, "clf")

    selector = RFE(classifier, step=step, n_features_to_select=num_features, verbose=1)

    selector.fit(X_train, y_train)

    # save vocaulary
    vocabulary = selector.named_steps["vectorizer"].vocabulary_
    with open(os.path.join("data", "vocabulary.txt"), "w") as f:
        for word, index in vocabulary.items():
            f.write(f"{word}\t{index}\n")

    print("Number of selected features: %d" % selector.n_features_)
    print("Selected features: %s" % selector.support_)
    print("Feature ranking: %s" % selector.ranking_)
    print("Accuracy: %f" % selector.score(X_test, y_test))
    print("Accuracy: %f" % selector.score(X_train, y_train))
    