
venv:
	python3.8 -m venv venv

Venv: venv 
	venv/bin/python -m pip install -r requirements-dev.txt


wheel:
	venv/bin/python setup.py develop
	venv/bin/python setup.py sdist
	venv/bin/python setup.py bdist_wheel

wheel-push:
	bash wheel-push.sh

pypi-package: wheel wheel-push

