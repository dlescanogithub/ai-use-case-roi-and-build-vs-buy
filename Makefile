# Plain equivalents (when make is absent):
#   python3 -m pip install -e ".[dev]"
#   python3 -m ruff check . && python3 -m ruff format --check .
#   python3 -m mypy
#   python3 -m pytest
#   ROI_ENABLE_REAL_PROVIDER=0 DECIDE_REAL_PROVIDER=0 python3 -m roi_and_build_vs_buy.evalkit
#   ROI_ENABLE_REAL_PROVIDER=0 python3 -m roi_and_build_vs_buy.evalkit.roi_regression
#   DECIDE_REAL_PROVIDER=0 python3 -m roi_and_build_vs_buy.evalkit.decide_regression
#   ROI_ENABLE_REAL_PROVIDER=0 ROI_PROVIDER=template python3 -m roi_and_build_vs_buy roi demo
#   python3 -m roi_and_build_vs_buy decide report --case examples/bruma_freight --out out/bruma-freight-report.md
#   python3 -m roi_and_build_vs_buy.secretscan .

PYTHON ?= python3
export ROI_ENABLE_REAL_PROVIDER ?= 0
export DECIDE_REAL_PROVIDER ?= 0

.PHONY: setup lint format typecheck test eval demo eval-regression secrets secretscan-hash

setup:
	$(PYTHON) -m pip install -e ".[dev]"

lint:
	$(PYTHON) -m ruff check .
	$(PYTHON) -m ruff format --check .

format:
	$(PYTHON) -m ruff format .
	$(PYTHON) -m ruff check --fix .

typecheck:
	$(PYTHON) -m mypy

test:
	$(PYTHON) -m pytest

eval:
	ROI_ENABLE_REAL_PROVIDER=0 DECIDE_REAL_PROVIDER=0 $(PYTHON) -m roi_and_build_vs_buy.evalkit

# Both forced regressions are supposed to exit non-zero. This target exits 1
# when both do, and exits 0 when either one passes (the gate went blind).
# CI treats a zero from this target as a failure.
eval-regression:
	@set +e; \
	ROI_ENABLE_REAL_PROVIDER=0 $(PYTHON) -m roi_and_build_vs_buy.evalkit.roi_regression; roi=$$?; \
	DECIDE_REAL_PROVIDER=0 $(PYTHON) -m roi_and_build_vs_buy.evalkit.decide_regression; decide=$$?; \
	echo "roi-regression exit $$roi"; \
	echo "decide-regression exit $$decide"; \
	if [ "$$roi" -eq 0 ] || [ "$$decide" -eq 0 ]; then exit 0; else exit 1; fi

demo:
	ROI_ENABLE_REAL_PROVIDER=0 ROI_PROVIDER=template $(PYTHON) -m roi_and_build_vs_buy roi demo
	mkdir -p out
	$(PYTHON) -m roi_and_build_vs_buy decide report --case examples/bruma_freight --out out/bruma-freight-report.md --adr-id 0002 --adr-out out/bruma-freight-adr.md

secrets: secretscan-hash
	$(PYTHON) -m roi_and_build_vs_buy.secretscan .

secretscan-hash:
	$(PYTHON) -c "import hashlib, pathlib, sys; digest = hashlib.sha256(pathlib.Path('src/roi_and_build_vs_buy/secretscan.py').read_bytes()).hexdigest(); text = pathlib.Path('docs/PROVENANCE.md').read_text(encoding='utf-8'); print(digest); sys.exit(0 if digest in text else 1)"
