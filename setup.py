import setuptools
import versioneer

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dotscience",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author="Subtree, Inc",
    author_email="support@dotscience.com",
    description="Tools for writing Dotscience workloads",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dotmesh-io/dotscience-python",
    packages=setuptools.find_packages(),
    install_requires=['jsonrpcclient[requests]', 'requests', 'datadots-api>=0.2.1'],
    tests_require=['pytest', 'hypothesis', 'jsonrpcclient[requests]', 'requests', 'datadots-api>=0.2.1'],
    zip_safe=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)
