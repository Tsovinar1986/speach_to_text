VENV := venv
ifeq ($(OS),Windows_NT)
	PYTHON := $(VENV)/Scripts/python.exe
	PIP := $(VENV)/Scripts/pip.exe
else
	PYTHON := $(VENV)/bin/python3
	PIP := $(VENV)/bin/pip
endif

HOST ?= 0.0.0.0
PORT ?= 8008

.PHONY: install run dev stop clean

$(VENV):
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

install: $(VENV)

run: install
	$(PYTHON) -m uvicorn app.main:app --host $(HOST) --port $(PORT)

dev: install
	$(PYTHON) -m uvicorn app.main:app --host $(HOST) --port $(PORT) --reload

stop:
	- pkill -f "uvicorn app.main:app" 2>/dev/null || true

clean:
	rm -rf $(VENV) app/__pycache__
