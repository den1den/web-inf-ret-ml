from sklearn.ensemble import ExtraTreesClassifier
from sklearn.feature_selection import SelectFromModel
from sklearn.pipeline import Pipeline


def test_task():
    # Example from http://scikit-learn.org/stable/modules/feature_selection.html
    from sklearn.datasets import load_iris
    from sklearn.svm import LinearSVC
    iris_data = load_iris()
    # iris_data is sklearn.datasets.base.Bunch
    X, y = iris_data.data, iris_data.target
    print(X.shape)
    clf = Pipeline([
        ('feature_selection', SelectFromModel(LinearSVC(penalty="l1", dual=False))),
        ('classification', ExtraTreesClassifier())
    ])
    clf.fit(X, y)
    y_pred = clf.predict(X)
    print(y_pred)
