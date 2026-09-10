PYTHON := python3
PIP := pip
VENV_STAMP := .install_stamp

.PHONY: all run debug clean lint lint-strict

all: $(VENV_STAMP)

# Only runs pip install if requirements.txt is newer than the stamp file
$(VENV_STAMP): requirements.txt
	$(PIP) install -r requirements.txt
	@touch $(VENV_STAMP)

install: $(VENV_STAMP)

run: $(VENV_STAMP)
	$(PYTHON) pac_man.py config.json

debug: $(VENV_STAMP)
	$(PYTHON) -m pdb pac_man.py config.json

clean:
	rm -rf __pycache__ src/__pycache__ tests/__pycache__ .mypy_cache $(VENV_STAMP)
	find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true

lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 .
	mypy . --strict