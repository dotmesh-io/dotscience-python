import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dotscience",
    version="0.0.1",
    author="Subtree, Inc",
# FIXME    author_email="author@example.com",
    description="Tools for writing Dotscience workloads",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dotmesh-io/dotscience-python",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
# FIXME        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
