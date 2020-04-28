.PHONY: generate-ipynb
generate-ipynb:
	jupytext --to notebook dotscience/model-template-files/*.predict.py

.PHONY: install-local
install-local: generate-ipynb
	python setup.py sdist
	pip3 install dist/dotscience-*.tar.gz

.PHONY: test
test: generate-ipynb
	pip3 install --upgrade pip setuptools wheel pytest hypothesis
	pip3 install .
	pytest dotscience
