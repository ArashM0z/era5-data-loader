.PHONY: install dev lint test docker clean
install: ; pip install -e .
dev: ; pip install -e ".[dev]"
cds: ; pip install -e ".[dev,cds]"
lint: ; ruff check src tests
test: ; pytest --cov=era5 --cov-report=term-missing
docker: ; docker build -t era5-loader:latest .
clean: ; rm -rf build dist *.egg-info .pytest_cache .ruff_cache
