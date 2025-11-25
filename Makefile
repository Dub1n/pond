PYTHON := $(shell if [ -x .venv/bin/python ]; then echo .venv/bin/python; else echo python3; fi)

.PHONY: test

# Run the full unittest suite (relationship + legacy)
test:
	$(PYTHON) -m unittest discover
