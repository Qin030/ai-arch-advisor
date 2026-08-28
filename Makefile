.PHONY: install dev api ui demo test lint fmt kb-check index eval clean

install:
	pip install -e ".[dev]"

# 給人看的：起 API 與 UI（兩個終端機）
api:
	uvicorn app.main:app --reload --port 8000

ui:
	streamlit run ui/app.py --server.port 8501

dev: api

# 給機器看的：端到端 smoke test。收工前必須綠燈
demo:
	pytest tests/smoke -q

test:
	pytest -q

lint:
	ruff check .

fmt:
	ruff format .

kb-check:
	python scripts/validate_kb.py

index:
	python scripts/build_index.py

eval:
	python scripts/run_eval.py --out docs/eval-report.md

clean:
	rm -rf .pytest_cache .ruff_cache .chroma __pycache__
