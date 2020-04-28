import setuptools
import glob
import os

with open("README.md", "r") as fh:
    long_description = fh.read()

def ensure_ipynb():
    """
    Make sure all generated .ipynb are newer than their corresponding source .py
    file.
    """
    for py in glob.glob("dotscience/files/*.predict.py"):
        ipynb = py[:-2] + "ipynb"
        if not os.path.exists():
            return False
        if os.stat(py).mtime >= os.stat(ipynb).mtime:
            return False
    return True
if not ensure_ipynb():
    raise SystemExit("Notebooks out of date, please run: make generate-ipynb")

setuptools.setup(
    name="dotscience",
    version="0.8.7",
    author="Subtree, Inc",
    author_email="support@dotscience.com",
    description="Tools for writing Dotscience workloads",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dotmesh-io/dotscience-python",
    packages=setuptools.find_packages(),
    install_requires=['datadots-api>=0.2.1', 'requests', "joblib==0.14.0"],
    tests_require=['pytest', 'hypothesis', 'datadots-api>=0.2.1'],
    zip_safe=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)
