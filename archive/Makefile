.PHONY: render-diagrams clean-diagram-build venv

VENV=.venv-diagrams
PY=$(VENV)/bin/python
PIP=$(VENV)/bin/pip

venv:
	python3 -m venv $(VENV)
	$(PIP) install -U pip
	$(PIP) install -r requirements-diagrams.txt

render-diagrams: venv
	$(PY) scripts/render_diagrams.py

generate-deck: venv
	$(PY) scripts/generate_deck_diagrams.py diagrams/specs/deck-framing.yaml

clean-diagram-build:
	rm -rf $(VENV)
	rm -rf diagrams/svg
	rm -rf diagrams/rendered
