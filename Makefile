install-local:
	python setup.py sdist
	pip3 install dist/dotscience-*.tar.gz 

test:
	pip3 install --upgrade pip setuptools wheel pytest hypothesis
	pip3 install .
	pytest dotscience