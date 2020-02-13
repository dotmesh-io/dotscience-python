import dotscience as ds
import os
import shutil
import sklearn
from sklearn import svm
from sklearn import datasets
from pickle import dump

if os.path.isdir("model"):
    shutil.rmtree("model", ignore_errors=True)
os.mkdir("model")
os.chdir("model")

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

dump(clf, open("model.joblib", "wb"))

# copy file into the model dir for the upload
shutil.copyfile("../classes_iris.json", ds.output("classes.json"))

ds.model(sklearn, "iris", ds.output("model.joblib"), classes="classes.json")

ds.publish("trained iris model", deploy=True)
