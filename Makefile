
.PHONY: all
all: check format

.PHONY: streamlit
streamlit:
	streamlit run main.py

.PHONY: check
check:
	ruff check .
	pyright .

.PHONY: format
format:
	ruff check --select I --fix
	ruff format

.PHONY: venv
venv:
	python3 -m venv venv
	. venv/bin/activate
	pip install -r requirements.txt