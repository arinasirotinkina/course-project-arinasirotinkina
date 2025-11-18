# Build stage
FROM python:3.11-slim AS build
WORKDIR /app
COPY requirements.txt requirements-dev.txt ./
RUN pip install --upgrade pip && \
    pip install --prefix=/install --no-cache-dir \
        -r requirements.txt -r requirements-dev.txt
COPY . .
RUN pytest -q

# Runtime stage
FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1
WORKDIR /app
RUN groupadd -r app && useradd -r -g app app
COPY --from=build /install /usr/local/
COPY --chown=app:app . .
VOLUME ["/app/data"]
EXPOSE 8000
HEALTHCHECK --interval=20s --timeout=3s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1
USER app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
