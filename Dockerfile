FROM python:3.12-slim
WORKDIR /app
# curl is needed for Coolify's HTTP health check probe (slim has none)
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p /app/data
ENV FASTSKILLS_ENV=production FASTSKILLS_PORT=5024 FASTSKILLS_DB=/app/data/fastskills.sqlite FASTSME_AUTH_DB=/app/data/fastskills-accounts.sqlite
EXPOSE 5024
HEALTHCHECK --interval=15s --timeout=5s --start-period=20s --retries=5 \
    CMD curl --fail http://127.0.0.1:5024/health || exit 1
CMD ["python", "app.py"]
