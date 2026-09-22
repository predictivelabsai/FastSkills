FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p /app/data
ENV FASTSKILLS_ENV=production FASTSKILLS_PORT=5024 FASTSKILLS_DB=/app/data/fastskills.sqlite FASTSME_AUTH_DB=/app/data/fastskills-accounts.sqlite
EXPOSE 5024
CMD ["python", "app.py"]
