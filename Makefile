.PHONY: install run test lint clean

install:
	pip install -e .

run:
	uvicorn src.main:app --reload

test:
	python3 -m pytest tests/ -v

lint:
	python3 -m py_compile src/main.py
	python3 -m py_compile src/api/routes.py
	python3 -m py_compile src/core/config.py
	python3 -m py_compile src/models/data.py
	python3 -m py_compile src/services/ingestion.py

clean:
	rm -rf __pycache__ .pytest_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
