FROM python:3.12-slim

LABEL org.opencontainers.image.title="ai-use-case-roi-and-build-vs-buy"

WORKDIR /app

COPY pyproject.toml README.md LICENSE ./
COPY src ./src
COPY assumptions ./assumptions
COPY examples ./examples
COPY evals ./evals

RUN pip install --no-cache-dir .

ENV ROI_ENABLE_REAL_PROVIDER=0 \
    ROI_PROVIDER=template \
    DECIDE_REAL_PROVIDER=0 \
    DECIDE_LOG_LEVEL=INFO \
    PYTHONDONTWRITEBYTECODE=1

ENTRYPOINT ["python", "-m", "roi_and_build_vs_buy"]
CMD ["--help"]
