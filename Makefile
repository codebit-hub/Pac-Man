PYTHON := python3
PIP := pip3
VENV_DIR := venv
VENV_STAMP := .install_stamp
FLAKE8 := flake8
MYPY := mypy

.PHONY: all run debug clean lint lint-strict build

all: $(VENV_STAMP)

$(VENV_STAMP): requirements.txt
	test -d $(VENV_DIR) || $(PYTHON) -m venv $(VENV_DIR)
	./$(VENV_DIR)/bin/$(PIP) install --upgrade pip
	./$(VENV_DIR)/bin/$(PIP) install -r requirements.txt
	@touch $(VENV_STAMP)

install: $(VENV_STAMP)

run: $(VENV_STAMP)
	./$(VENV_DIR)/bin/python3 pac-man.py config.json

debug: $(VENV_STAMP)
	./$(VENV_DIR)/bin/python3 -m pdb pac-man.py config.json

clean:
	rm -rf __pycache__ src/__pycache__
	rm -rf .mypy_cache $(VENV_STAMP) $(BUILD_STAMP)
	find . -type d -name "__pycache__" -exec rm -rf {} + \
		2>/dev/null || true

fclean: clean
	rm -rf $(VENV_DIR) $(VENV_STAMP)

lint: $(VENV_STAMP)
	./$(VENV_DIR)/bin/$(FLAKE8) .
	./$(VENV_DIR)/bin/$(MYPY) .

lint-strict: $(VENV_STAMP)
	./$(VENV_DIR)/bin/$(FLAKE8) .
	./$(VENV_DIR)/bin/$(MYPY) . --strict

BUILD_STAMP := .build_stamp

build: $(BUILD_STAMP)

$(BUILD_STAMP): $(VENV_STAMP) pac-man.py config.json HOW_TO_PLAY.txt
	@echo "Installing PyInstaller..."
	./$(VENV_DIR)/bin/$(PIP) install pyinstaller
	@echo "Building the standalone executable..."
	./$(VENV_DIR)/bin/pyinstaller \
		--noconfirm \
		--onedir \
		--windowed \
		--name "pac-man" \
		--paths src \
		--add-data "assets:assets" \
		--add-data "config.json:." \
		pac-man.py
	@cp HOW_TO_PLAY.txt dist/pac-man/
	@touch $(BUILD_STAMP)
	@echo "Build complete! Zip 'dist/pac-man/' folder. "
	@echo "Upload it to Itch.io."
