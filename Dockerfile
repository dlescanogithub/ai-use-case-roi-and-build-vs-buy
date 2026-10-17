FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml README.md LICENSE ./
COPY src ./src
COPY assumptions ./assumptions
COPY evals ./evals

RUN pip install --no-cache-dir .

ENV ROI_ENABLE_REAL_PROVIDER=0 \
    ROI_PROVIDER=template \
    PYTHONDONTWRITEBYTECODE=1

CMD ["python", "-m", "roi_model.cli", "demo"]
