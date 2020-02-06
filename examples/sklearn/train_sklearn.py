import dotscience as ds
import os
import shutil
import sklearn
from sklearn import svm
from sklearn import datasets
from joblib import dump

ds.connect(
    os.getenv("DOTSCIENCE_USERNAME"), 
    os.getenv("DOTSCIENCE_APIKEY"), 
    os.getenv("DOTSCIENCE_PROJECT_NAME"),
    os.getenv("DOTSCIENCE_URL")
)

clf = svm.SVC(gamma='scale', probability=True)
iris = datasets.load_iris()
X, y = iris.data, iris.target
clf.fit(X, y)

dump(clf, 'model.joblib')

ds.model(sklearn, "iris", ds.output('model.joblib'))

ds.publish("trained iris model", deploy=True)
