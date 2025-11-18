# Build stage
FROM python:3.11-slim AS build
WORKDIR /app
COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements-dev.txt && \
    pip install --no-cache-dir pytest
COPY . .
RUN pytest -q

# Runtime stage
FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app
RUN useradd -m appuser
COPY --from=build /usr/local/lib/python3.11 /usr/local/lib/python3.11
COPY --from=build /usr/local/bin /usr/local/bin
COPY . .
EXPOSE 8000
HEALTHCHECK CMD curl -f http://localhost:8000/health || exit 1
USER appuser
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
