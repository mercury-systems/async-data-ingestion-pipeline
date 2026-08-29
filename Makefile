.PHONY: install run test test-all lint clean demo

install:
	pip install -e .

run:
	uvicorn src.main:app --reload

test:
	python3 -m pytest tests/ -v -m 'not integration'

test-all:
	python3 -m pytest tests/ -v

lint:
	python3 -m py_compile src/main.py src/api/routes.py src/core/config.py src/core/circuit_breaker.py src/models/data.py src/services/ingestion.py src/services/job_store.py src/services/metrics.py src/services/batch_processor.py

clean:
	rm -rf __pycache__ .pytest_cache *.db src/*.egg-info dist build
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

demo:
	python3 -m src.demo
