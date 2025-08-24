FROM python:3.12-slim

WORKDIR /app

# Install deps
RUN apt-get update && apt-get install -y build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Default envs
ENV PYTHONUNBUFFERED=1

CMD ["gunicorn", "backend.wsgi:application", "--bind", "0.0.0.0:8000"]
