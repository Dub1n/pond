.PHONY: render-diagrams clean-diagram-build venv

MAKEFILE_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
ROOT := $(abspath $(MAKEFILE_DIR)/..)
VENV := $(ROOT)/.venv
REQ := $(ROOT)/requirements.txt
PY := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

venv:
	python3 -m venv $(VENV)
	$(PIP) install -U pip
	$(PIP) install -r $(REQ)

render-diagrams: venv
	$(PY) scripts/render_diagrams.py

generate-deck: venv
	$(PY) scripts/generate_deck_diagrams.py diagrams/specs/deck-framing.yaml

clean-diagram-build:
	rm -rf $(VENV)
	rm -rf diagrams/svg
	rm -rf diagrams/rendered
