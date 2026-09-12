PYTHON := python3
PIP := pip3
VENV_DIR := venv
VENV_STAMP := .install_stamp
FLAKE8 := flake8
MYPY := mypy

.PHONY: all run debug clean lint lint-strict

all: $(VENV_STAMP)

$(VENV_STAMP): requirements.txt
	test -d $(VENV_DIR) || $(PYTHON) -m venv $(VENV_DIR)
	./$(VENV_DIR)/bin/$(PIP) install --upgrade pip
	./$(VENV_DIR)/bin/$(PIP) install -r requirements.txt	
	@touch $(VENV_STAMP)

install: $(VENV_STAMP)

run: $(VENV_STAMP)
	./$(VENV_DIR)/bin/python3 pac_man.py config.json

debug: $(VENV_STAMP)
	./$(VENV_DIR)/bin/python3 -m pdb pac_man.py config.json

clean:
	rm -rf __pycache__ src/__pycache__ 
	rm -rf .mypy_cache $(VENV_STAMP)
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

fclean: clean
	rm -rf $(VENV_DIR) $(VENV_STAMP)

lint: $(VENV_STAMP)
	./$(VENV_DIR)/bin/$(FLAKE8) .
	./$(VENV_DIR)/bin/$(MYPY) . --warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs \
		--check-untyped-defs

lint-strict: $(VENV_STAMP)
	./$(VENV_DIR)/bin/$(FLAKE8) .
	./$(VENV_DIR)/bin/$(MYPY) . --strict