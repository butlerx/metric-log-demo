VERSION=1.0.0
PYTHON=python3

run: requirements
	$(PYTHON) src

.PHONY: clean
clean:
	rm -rf dist/ build/ *.egg-info/ test/logs test/results .coverage*
	find . -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete

## Upgrade requirements file
.PHONY: requirements
requirements:
	$(PYTHON) -m pip install --user -r requirements.txt
