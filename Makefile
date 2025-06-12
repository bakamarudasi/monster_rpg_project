.PHONY: install test

install:
	pip install -e .

test: install
	pytest
