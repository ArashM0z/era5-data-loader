FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    libnetcdf-dev build-essential git \
 && rm -rf /var/lib/apt/lists/*
COPY pyproject.toml ./
COPY src ./src
COPY README.md LICENSE ./
RUN pip install --upgrade pip setuptools wheel && pip install -e ".[dev]"
ENTRYPOINT ["era5-fetch"]
