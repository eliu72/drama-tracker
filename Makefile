lint: 
	black .
	flake8 .

test: lint 
	pytest

shell:
	poetry shell

install: 
	poetry install --no-dev

install-dev:
	poetry install